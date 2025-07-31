from api.event import EventoConversao
from supabase_conn import get_connection
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def salvar_evento(evento: EventoConversao):
    """
    Salva o evento no banco Supabase (PostgreSQL), utilizando a tabela 'eventos'.
    Agora também salva event_id e ga_id.
    """

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO eventos (
            nome,
            sobrenome,
            email,
            telefone,
            user_id,
            ip,
            user_agent,
            url,
            referrer,
            pagina_destino,
            botao_clicado,
            gclid,
            fbclid,
            fbp,
            fbc,
            cidade,
            regiao,
            pais,
            campanha,
            origem,
            evento,
            visitor_id,
            consentimento,
            event_id,
            ga_id
        ) VALUES (
            %(nome)s, %(sobrenome)s, %(email)s, %(telefone)s, %(user_id)s,
            %(ip)s, %(user_agent)s, %(url)s, %(referrer)s, %(pagina_destino)s, %(botao_clicado)s,
            %(gclid)s, %(fbclid)s, %(fbp)s, %(fbc)s,
            %(cidade)s, %(regiao)s, %(pais)s, %(campanha)s,
            %(origem)s, %(evento)s, %(visitor_id)s, %(consentimento)s,
            %(event_id)s, %(ga_id)s
        )
    """

    # Aceita tanto objeto Pydantic quanto dict
    evento_dict = evento.dict() if hasattr(evento, "dict") else evento

    cursor.execute(sql, {
        "nome": evento_dict.get("nome"),
        "sobrenome": evento_dict.get("sobrenome"),
        "email": evento_dict.get("email"),
        "telefone": evento_dict.get("telefone"),
        "user_id": evento_dict.get("user_id"),
        "ip": evento_dict.get("ip"),
        "user_agent": evento_dict.get("user_agent"),
        "url": evento_dict.get("url"),
        "referrer": evento_dict.get("referrer"),
        "pagina_destino": evento_dict.get("pagina_destino"),
        "botao_clicado": evento_dict.get("botao_clicado"),
        "gclid": evento_dict.get("gclid"),
        "fbclid": evento_dict.get("fbclid"),
        "fbp": evento_dict.get("fbp"),
        "fbc": evento_dict.get("fbc"),
        "cidade": evento_dict.get("cidade"),
        "regiao": evento_dict.get("regiao"),
        "pais": evento_dict.get("pais"),
        "campanha": evento_dict.get("campanha"),
        "origem": evento_dict.get("origem"),
        "evento": evento_dict.get("evento"),
        "visitor_id": evento_dict.get("visitor_id"),
        "consentimento": evento_dict.get("consentimento"),
        "event_id": evento_dict.get("event_id"),
        "ga_id": evento_dict.get("ga_id"),
    })

    conn.commit()
    conn.close()
