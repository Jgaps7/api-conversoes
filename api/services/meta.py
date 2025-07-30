import time
import hashlib
import httpx
from supabase_conn import get_connection
from api.event import EventoConversao
from utils.logger import log_sucesso_meta, log_erro_meta
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def hash_dado(valor):
    if valor and isinstance(valor, str):
        return hashlib.sha256(valor.strip().lower().encode()).hexdigest()
    return None

def carregar_credenciais_meta(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chave, valor FROM credenciais 
        WHERE user_id = %s AND plataforma = 'meta'
    """, (user_id,))
    dados = dict(cursor.fetchall())
    conn.close()
    return dados

# Função extra para aceitar dict ou objeto
def get_attr(evento, campo, default=None):
    if isinstance(evento, dict):
        return evento.get(campo, default)
    return getattr(evento, campo, default)

async def enviar_para_meta(evento):
    try:
        user_id = get_attr(evento, "user_id")
        if not user_id:
            return {"erro": "user_id não informado no evento."}

        cred = carregar_credenciais_meta(user_id)
        if "pixel_id" not in cred or "access_token" not in cred:
            return {"erro": "Credenciais da Meta ausentes ou incompletas para este usuário."}

        pixel_id = cred["pixel_id"]
        access_token = cred["access_token"]

        user_data = {k: v for k, v in {
            "em": hash_dado(get_attr(evento, "email")),
            "ph": hash_dado(get_attr(evento, "telefone")),
            "fn": hash_dado(get_attr(evento, "nome")),
            "ln": hash_dado(get_attr(evento, "sobrenome")),
            "client_ip_address": get_attr(evento, "ip"),
            "client_user_agent": get_attr(evento, "user_agent"),
            "fbc": get_attr(evento, "fbc") or get_attr(evento, "fbclid"),
            "fbp": get_attr(evento, "fbp"),
            "external_id": get_attr(evento, "visitor_id") or user_id
        }.items() if v is not None}

        custom_data = {k: v for k, v in {
            "utm_source": get_attr(evento, "utm_source"),
            "utm_medium": get_attr(evento, "utm_medium"),
            "utm_campaign": get_attr(evento, "utm_campaign"),
            "referer": get_attr(evento, "referrer"),
            "page": get_attr(evento, "pagina_destino"),
            "button": get_attr(evento, "botao_clicado"),
            "value": 1.0,
            "currency": "BRL"
        }.items() if v is not None}

        payload = {
            "data": [{
                "event_name": get_attr(evento, "evento"),
                "event_time": int(time.time()),
                "event_source_url": get_attr(evento, "url") or "https://seusite.com",
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
