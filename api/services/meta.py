import time
import hashlib
import httpx
from supabase_conn import get_connection
from api.event import EventoConversao
from utils.logger import log_sucesso_meta, log_erro_meta
from streamlit.runtime.scriptrunner import get_script_run_ctx
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def hash_dado(valor):
    """Aplica hash SHA-256 exigido pela Meta Ads."""
    if valor and isinstance(valor, str):
        return hashlib.sha256(valor.strip().lower().encode()).hexdigest()
    return None


def carregar_credenciais_meta(email_usuario):
    """Busca as credenciais da conta Meta Ads do usuário no banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chave, valor FROM credenciais 
        WHERE email_usuario = ? AND plataforma = 'meta'
    """, (email_usuario,))
    dados = dict(cursor.fetchall())
    conn.close()
    return dados


async def enviar_para_meta(evento: EventoConversao):
    """Envia evento de conversão para a Meta Conversions API."""
    try:
        # Recupera e-mail do usuário da sessão ativa
        ctx = get_script_run_ctx()
        email_usuario = ctx.session_state.get("email")

        cred = carregar_credenciais_meta(email_usuario)

        # Validação de credenciais mínimas
        if "pixel_id" not in cred or "access_token" not in cred:
            raise ValueError("Credenciais da Meta ausentes ou incompletas para este usuário.")

        pixel_id = cred["pixel_id"]
        access_token = cred["access_token"]

        # Dados do usuário (hash ou identificadores)
        user_data = {k: v for k, v in {
            "em": hash_dado(evento.email),
            "ph": hash_dado(evento.telefone),
            "fn": hash_dado(evento.nome),
            "client_ip_address": evento.ip,
            "client_user_agent": evento.user_agent,
            "fbc": evento.fbclid,
            "fbp": evento.user_id,
            "external_id": getattr(evento, "click_id", None)
        }.items() if v is not None}

        # Dados de campanha (utm e referer)
        custom_data = {k: v for k, v in {
            "utm_source": getattr(evento, "utm_source", None),
            "utm_medium": getattr(evento, "utm_medium", None),
            "utm_campaign": getattr(evento, "utm_campaign", None),
            "referer": evento.referrer
        }.items() if v is not None}

        payload = {
            "data": [{
                "event_name": evento.evento,
                "event_time": int(time.time()),
                "event_source_url": evento.url or "https://site.com",
                "action_source": "website",
                "user_data": user_data,
                "custom_data": custom_data
            }]
        }

        url = f"https://graph.facebook.com/v17.0/{pixel_id}/events"
        params = {"access_token": access_token}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()
            resultado = response.json()
            log_sucesso_meta(resultado, evento)
            return resultado

    except Exception as e:
        log_erro_meta(str(e), evento)
        return {"erro": str(e)}
