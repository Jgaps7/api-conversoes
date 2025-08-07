from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
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

load_dotenv()

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
from utils.config import get_envio_ativado

gerar_google_ads_yaml()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="API de Conversões Google/Meta", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://casadosbolosandrade.com.br",
        "https://www.casadosbolosandrade.com.br"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return JSONResponse(status_code=204)

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

def validar_api_key(email: str, plataforma: str, api_key: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False
    user_id = user[0]
    cursor.execute("""
        SELECT 1 FROM credenciais
        WHERE user_id = %s AND plataforma = %s AND chave = 'api_key' AND valor = %s
    """, (user_id, plataforma, api_key))
    resultado = cursor.fetchone()
    conn.close()
    return bool(resultado)

@app.post("/conversao")
@limiter.limit("100/minute")
async def receber_conversao(
    request: Request,
    evento: EventoConversao,
    x_api_key: Optional[str] = Header(None)
):
    try:
        origens_validas = ("google", "meta", "cookies", "site")
        if evento.origem not in origens_validas:
            raise HTTPException(
                status_code=400,
                detail=f"Origem inválida: use {', '.join(origens_validas)}."
            )

        # Eventos anônimos (cookies ou site)
        if evento.origem in ("cookies", "site"):
            salvar_evento(evento)
            return {"status": "recebido", "detalhes": "Lead anônimo armazenado (cookies/site)."}

        # Eventos autenticados (google ou meta)
        if not x_api_key:
            raise HTTPException(status_code=401, detail="Header 'x-api-key' ausente.")
        if not evento.email:
            salvar_evento(evento)
            return {"status": "recebido", "detalhes": "Evento armazenado sem envio por falta de email."}

        if not validar_api_key(evento.email, evento.origem, x_api_key):
            raise HTTPException(status_code=403, detail="API Key inválida para esse usuário ou plataforma.")

        salvar_evento(evento)

        # Novo: controle se envio está ativado
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT envio_ativado FROM users WHERE email = %s", (evento.email,))
        res = cursor.fetchone()
        conn.close()

        resultado = None
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
            return {"status": "sucesso", "detalhes": resultado}
        else:
            return {"status": "recebido", "detalhes": "Envio desativado para este cliente. Evento armazenado com sucesso."}

    except Exception as e:
        try:
            payload = await request.body()
            print("=====> [DEBUG] Payload bruto recebido:", payload)
        except Exception as ee:
            print("[ERRO] Falha ao ler payload bruto:", str(ee))
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/status")
def verificar_status_envio(email: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT envio_ativado FROM users WHERE email = %s", (email,))
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
