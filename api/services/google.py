import os
import sys
import hashlib
import datetime
from supabase_conn import get_connection
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.config import load_from_dict

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from api.event import EventoConversao
from utils.logger import log_sucesso_google, log_erro_google


def hash_dado(dado):
    """Aplica hash SHA-256 ao dado, se ele existir (usado para email/telefone)."""
    if dado:
        return hashlib.sha256(dado.strip().lower().encode()).hexdigest()
    return None


def carregar_credenciais_google(email_usuario):
    """
    Busca as credenciais da conta Google Ads vinculadas ao usuário no banco PostgreSQL.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chave, valor FROM credenciais 
        WHERE email_usuario = %s AND plataforma = 'google'
    """, (email_usuario,))

    dados = dict(cursor.fetchall())
    conn.close()
    return dados


async def enviar_para_google(evento: EventoConversao):
    """
    Envia evento de conversão para a API do Google Ads usando o ConversionUploadService.
    """
    try:
        # Pega o email do usuário logado via contexto de execução do Streamlit
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        email_usuario = ctx.session_state.get("email")

        # Carrega credenciais do usuário
        cred = carregar_credenciais_google(email_usuario)

        if not cred:
            return {"erro": "Credenciais do Google não encontradas para este usuário."}

        # Monta configuração do cliente Google Ads
        config_dict = {
            "developer_token": cred["developer_token"],
            "client_id": cred["client_id"],
            "client_secret": cred["client_secret"],
            "refresh_token": cred["refresh_token"],
            "login_customer_id": cred["login_customer_id"]
        }

        client = GoogleAdsClient(load_from_dict(config_dict))

        # 🆔 Define o recurso de conversão
        conversion_action = (
            f"customers/{cred['customer_id']}/conversionActions/{cred['conversion_action_id']}"
        )

        # Monta a conversão
        conversion = client.get_type("ClickConversion")
        conversion.conversion_action = conversion_action
        conversion.conversion_date_time = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S%z")
        conversion.conversion_value = 1.0
        conversion.currency_code = "BRL"

        # Define identificador por GCLID ou dados do usuário
        if evento.gclid:
            conversion.gclid = evento.gclid
        else:
            user_identifier = client.get_type("UserIdentifier")
            if evento.email:
                user_identifier.hashed_email = hash_dado(evento.email)
            elif evento.telefone:
                user_identifier.hashed_phone_number = hash_dado(evento.telefone)
            conversion.user_identifiers.append(user_identifier)

        # Envia para a API do Google Ads
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
