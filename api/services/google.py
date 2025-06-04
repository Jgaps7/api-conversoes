import os
import hashlib
import datetime
import sqlite3
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.config import load_from_dict
from api.event import EventoConversao
from utils.logger import log_sucesso_google, log_erro_google

def hash_dado(dado):
    """Aplica SHA-256 no dado, se existir."""
    if dado:
        return hashlib.sha256(dado.strip().lower().encode()).hexdigest()
    return None

def carregar_credenciais_google(email_usuario):
    """Busca as credenciais da conta Google Ads do usuário no banco de dados."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chave, valor FROM credenciais 
        WHERE email_usuario = ? AND plataforma = 'google'
    """, (email_usuario,))
    dados = dict(cursor.fetchall())
    conn.close()
    return dados

async def enviar_para_google(evento: EventoConversao):
    """Envia conversão para Google Ads API usando ConversionUploadService."""
    try:
        # Pega e-mail do usuário logado pela sessão ativa do Streamlit
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        email_usuario = ctx.session_state.get("email")

        cred = carregar_credenciais_google(email_usuario)

        config_dict = {
            "developer_token": cred["developer_token"],
            "client_id": cred["client_id"],
            "client_secret": cred["client_secret"],
            "refresh_token": cred["refresh_token"],
            "login_customer_id": cred["login_customer_id"]
        }

        client = GoogleAdsClient(load_from_dict(config_dict))
        conversion_action = f"customers/{cred['customer_id']}/conversionActions/{cred['conversion_action_id']}"

        conversion = client.get_type("ClickConversion")
        conversion.conversion_action = conversion_action
        conversion.conversion_date_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")
        conversion.conversion_value = 1.0
        conversion.currency_code = "BRL"

        # Identificação por GCLID ou dados do usuário
        if evento.gclid:
            conversion.gclid = evento.gclid
        else:
            user_identifier = client.get_type("UserIdentifier")
            if evento.email:
                user_identifier.hashed_email = hash_dado(evento.email)
            elif evento.telefone:
                user_identifier.hashed_phone_number = hash_dado(evento.telefone)
            conversion.user_identifiers.append(user_identifier)

        service = client.get_service("ConversionUploadService")
        request = client.get_type("UploadClickConversionsRequest")
        request.customer_id = cred["customer_id"]
        request.conversions.append(conversion)
        request.partial_failure = False
        response = service.upload_click_conversions(request=request)

        resultado = {"mensagem": "Conversão enviada com sucesso.", "response": str(response)}
        log_sucesso_google(resultado, evento)
        return resultado

    except Exception as e:
        log_erro_google(str(e), evento)
        return {"erro": str(e)}
