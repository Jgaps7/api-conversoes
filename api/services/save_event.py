from api.event import EventoConversao
from supabase_conn import get_connection
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from api.event import EventoConversao
from supabase_conn import get_connection
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def salvar_evento(evento: EventoConversao):
    """
    Salva o evento no banco Supabase (PostgreSQL), utilizando a tabela 'eventos'.
    Agora trata campos opcionais, nunca envia None e inclui data/hora.
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
            ga_id,
            data_criacao
        ) VALUES (
            %(nome)s, %(sobrenome)s, %(email)s, %(telefone)s, %(user_id)s,
            %(ip)s, %(user_agent)s, %(url)s, %(referrer)s, %(pagina_destino)s, %(botao_clicado)s,
            %(gclid)s, %(fbclid)s, %(fbp)s, %(fbc)s,
            %(cidade)s, %(regiao)s, %(pais)s, %(campanha)s,
            %(origem)s, %(evento)s, %(visitor_id)s, %(consentimento)s,
            %(event_id)s, %(ga_id)s, %(data_criacao)s
        )
    """

    evento_dict = evento.dict() if hasattr(evento, "dict") else evento

    # Função para garantir valor default para cada campo
    def default_str(val):
        return val if val is not None else ""
    def default_bool(val):
        return bool(val) if val is not None else False

    params = {
        "nome": default_str(evento_dict.get("nome")),
        "sobrenome": default_str(evento_dict.get("sobrenome")),
        "email": default_str(evento_dict.get("email")),
        "telefone": default_str(evento_dict.get("telefone")),
        "user_id": default_str(evento_dict.get("user_id")),
        "ip": default_str(evento_dict.get("ip")),
        "user_agent": default_str(evento_dict.get("user_agent")),
        "url": default_str(evento_dict.get("url")),
        "referrer": default_str(evento_dict.get("referrer")),
        "pagina_destino": default_str(evento_dict.get("pagina_destino")),
        "botao_clicado": default_str(evento_dict.get("botao_clicado")),
        "gclid": default_str(evento_dict.get("gclid")),
        "fbclid": default_str(evento_dict.get("fbclid")),
        "fbp": default_str(evento_dict.get("fbp")),
        "fbc": default_str(evento_dict.get("fbc")),
        "cidade": default_str(evento_dict.get("cidade")),
        "regiao": default_str(evento_dict.get("regiao")),
        "pais": default_str(evento_dict.get("pais")),
        "campanha": default_str(evento_dict.get("campanha")),
        "origem": default_str(evento_dict.get("origem")),
        "evento": default_str(evento_dict.get("evento")),
        "visitor_id": default_str(evento_dict.get("visitor_id")),
        "consentimento": default_bool(evento_dict.get("consentimento")),
        "event_id": default_str(evento_dict.get("event_id")),
        "ga_id": default_str(evento_dict.get("ga_id")),
        # Horário UTC do Python (garante ordem e debug mesmo sem timezone)
        "data_criacao": datetime.utcnow()
    }

    print("[DEBUG] Evento a ser salvo no banco:", params)  # log para debug

    cursor.execute(sql, params)
    conn.commit()
    conn.close()
