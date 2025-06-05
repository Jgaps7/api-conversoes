from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import sqlite3

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Carrega variáveis de ambiente
load_dotenv()

# Importa serviços
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

# Gera o google-ads.yaml a partir do .env
gerar_google_ads_yaml()

# Inicializa a aplicação FastAPI
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="API de Conversões Google/Meta", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Modelo de dados esperado
class EventoConversao(BaseModel):
    email: Optional[str] = None
    telefone: Optional[str] = None
    nome: Optional[str] = None
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
    origem: str
    evento: str

# Função de validação da API Key
def validar_api_key(email: str, plataforma: str, api_key: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM credenciais 
        WHERE email_usuario = ? AND plataforma = ? AND api_key = ?
    """, (email, plataforma, api_key))
    resultado = cursor.fetchone()
    conn.close()
    return bool(resultado)

# Rota de conversão com verificação + limite de requisição por IP
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

        if evento.origem not in ("google", "meta"):
            raise HTTPException(status_code=400, detail="Origem inválida: use 'google' ou 'meta'.")

        if not x_api_key:
            raise HTTPException(status_code=401, detail="Header 'x-api-key' ausente.")

        if not evento.email:
            raise HTTPException(status_code=400, detail="Campo 'email' é obrigatório para autenticação.")

        if not validar_api_key(evento.email, evento.origem, x_api_key):
            raise HTTPException(status_code=403, detail="API Key inválida para esse usuário ou plataforma.")

        salvar_evento(evento)

        if evento.origem == "google":
            resultado = await enviar_para_google(evento)
            if "erro" in resultado:
                log_erro_google(resultado["erro"], evento)
            else:
                log_sucesso_google(resultado, evento)

        elif evento.origem == "meta":
            resultado = await enviar_para_meta(evento)
            if "erro" in resultado:
                log_erro_meta(resultado["erro"], evento)
            else:
                log_sucesso_meta(resultado, evento)

        print(f"[EVENTO ENVIADO] Resultado: {resultado}")
        return {"status": "sucesso", "detalhes": resultado}

    except Exception as e:
        print(f"[ERRO] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
