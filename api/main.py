from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel, Extra
from typing import Optional
from dotenv import load_dotenv
from supabase_conn import get_connection
from fastapi.responses import JSONResponse
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Carrega variáveis de ambiente
load_dotenv()

# Importações dos serviços e utilitários
from api.services.google import enviar_para_google
from api.services.meta import enviar_para_meta
from api.services.save_event import salvar_evento
from utils.logger import (
    log_evento_recebido,
    log_sucesso_google,
    log_erro_google,
    log_sucesso_meta,
    log_erro_meta
)
from utils.generate_google_yaml import gerar_google_ads_yaml
from utils.config import get_envio_ativado  # <- nova função de controle

# Gera o google-ads.yaml a partir do .env
gerar_google_ads_yaml()

# Inicializa a aplicação FastAPI
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="API de Conversões Google/Meta", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Modelo de dados esperado (agora aceita campos extras do JS automaticamente)
class EventoConversao(BaseModel, extra=Extra.allow):
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    user_id: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    url: Optional[str] = None
    referrer: Optional[str] = None
    pagina_destino: Optional[str] = None
    botao_clicado: Optional[str] = None
    gclid: Optional[str] = None
    fbclid: Optional[str] = None
    fbp: Optional[str] = None
    fbc: Optional[str] = None
    cidade: Optional[str] = None
    regiao: Optional[str] = None
    pais: Optional[str] = None
    campanha: Optional[str] = None
    origem: str
    evento: str
    visitor_id: Optional[str] = None  
    consentimento: Optional[bool] = None  

# Função de validação da API Key
def validar_api_key(email: str, plataforma: str, api_key: str):
    conn = get_connection()
    cursor = conn.cursor()
    print(f"===> Validação de API Key: email={email}, plataforma={plataforma}, api_key={api_key}")

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    print(f"===> Resultado SELECT id FROM users: {user}")

    if not user:
        print("===> Usuário não encontrado!")
        conn.close()
        return False

    user_id = user[0]
    print(f"===> user_id encontrado: {user_id}")

    cursor.execute("""
        SELECT 1 FROM credenciais
        WHERE user_id = %s AND plataforma = %s AND chave = 'api_key' AND valor = %s
    """, (user_id, plataforma, api_key))
    resultado = cursor.fetchone()
    print(f"===> Resultado SELECT na tabela credenciais: {resultado}")

    conn.close()
    return bool(resultado)

# ------------------------- ENDPOINT DE CONVERSÃO -------------------------
@app.post("/conversao")
@limiter.limit("100/minute")
async def receber_conversao(
    request: Request,
    evento: EventoConversao,
    x_api_key: Optional[str] = Header(None)
):
    try:
        print(f"[EVENTO RECEBIDO] Origem: {evento.origem} | Evento: {evento.evento}")
        log_evento_recebido(evento)

        origens_validas = ("google", "meta", "cookies", "site")
        if evento.origem not in origens_validas:
            raise HTTPException(
                status_code=400,
                detail=f"Origem inválida: use {', '.join(origens_validas)}."
            )

        # Leads anônimos (cookies/site) — não exigem email nem API Key
        if evento.origem in ("cookies", "site"):
            salvar_evento(evento)  # Passe o objeto Pydantic!
            return {"status": "recebido", "detalhes": "Lead anônimo armazenado (cookies/site)."}

        # Leads de Google/Meta — exige API Key e email
        if not x_api_key:
            raise HTTPException(status_code=401, detail="Header 'x-api-key' ausente.")
        if not evento.email:
            print("[INFO] Evento sem email — será armazenado, mas não enviado.")
            salvar_evento(evento)
            return {"status": "recebido", "detalhes": "Evento armazenado sem envio por falta de email."}

        if not validar_api_key(evento.email, evento.origem, x_api_key):
            raise HTTPException(status_code=403, detail="API Key inválida para esse usuário ou plataforma.")

        salvar_evento(evento)

        # ------------------------- NOVO CONTROLE POR USUÁRIO -------------------------
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT envio_ativado FROM users WHERE email = ?", (evento.email,))
        res = cursor.fetchone()
        conn.close()

        if res and res[0]:
            if evento.origem == "google":
                resultado = await enviar_para_google(evento.dict())
                if "erro" in resultado:
                    log_erro_google(resultado["erro"], evento.dict())
                else:
                    log_sucesso_google(resultado, evento.dict())

            elif evento.origem == "meta":
                resultado = await enviar_para_meta(evento.dict())
                if "erro" in resultado:
                    log_erro_meta(resultado["erro"], evento.dict())
                else:
                    log_sucesso_meta(resultado, evento.dict())

            print(f"[EVENTO ENVIADO] Resultado: {resultado}")
            return {"status": "sucesso", "detalhes": resultado}
        else:
            print("[EVENTO RECEBIDO] Envio desativado para este usuário - armazenado apenas.")
            return {"status": "recebido", "detalhes": "Envio desativado para este cliente. Evento armazenado com sucesso."}

    except Exception as e:
        print(f"[ERRO] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Status da API
@app.get("/status")
def verificar_status_envio(email: str):
    """
    Verifica se o envio de eventos está ativado para o usuário com base no email.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT envio_ativado FROM users WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        return JSONResponse(content={
            "email": email,
            "envio_ativado": bool(resultado[0])
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")
