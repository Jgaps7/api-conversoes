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
    """Aplica hash SHA-256 exigido pela Meta Ads (para email, telefone, nome)."""
    if valor and isinstance(valor, str):
        return hashlib.sha256(valor.strip().lower().encode()).hexdigest()
    return None


def carregar_credenciais_meta(user_id):
    """Busca as credenciais da conta Meta Ads do usuário via user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chave, valor FROM credenciais 
        WHERE user_id = %s AND plataforma = 'meta'
    """, (user_id,))
    dados = dict(cursor.fetchall())
    conn.close()
    return dados


async def enviar_para_meta(evento: EventoConversao):
    """Envia evento para a Meta Conversions API com dados completos do lead."""
    try:
        if not evento.user_id:
            return {"erro": "user_id não informado no evento."}

        cred = carregar_credenciais_meta(evento.user_id)

        # ⚠️ Verifica se as credenciais mínimas estão presentes
        if "pixel_id" not in cred or "access_token" not in cred:
            return {"erro": "Credenciais da Meta ausentes ou incompletas para este usuário."}

        pixel_id = cred["pixel_id"]
        access_token = cred["access_token"]

        # 🔐 Dados do usuário para identificação na Meta
        user_data = {k: v for k, v in {
            "em": hash_dado(evento.email),
            "ph": hash_dado(evento.telefone),
            "fn": hash_dado(evento.nome),
            "client_ip_address": evento.ip,
            "client_user_agent": evento.user_agent,
            "fbc": evento.fbc or evento.fbclid,
            "fbp": evento.fbp or evento.user_id,
            "external_id": evento.user_id or evento.visitor_id
        }.items() if v is not None}

        # 📊 Dados adicionais de campanha
        custom_data = {k: v for k, v in {
            "utm_source": getattr(evento, "utm_source", None),
            "utm_medium": getattr(evento, "utm_medium", None),
            "utm_campaign": getattr(evento, "utm_campaign", None),
            "referer": evento.referrer,
            "page": evento.pagina_destino,
            "button": evento.botao_clicado
        }.items() if v is not None}

        # 📦 Payload enviado para a Meta
        payload = {
            "data": [{
                "event_name": evento.evento,
                "event_time": int(time.time()),
                "event_source_url": evento.url or "https://seusite.com",
                "action_source": "website",
                "user_data": user_data,
                "custom_data": custom_data
            }]
        }

        # Envio da requisição para a Meta CAPI
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
