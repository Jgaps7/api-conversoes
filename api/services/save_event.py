from api.event import EventoConversao
from supabase_conn import get_connection
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def salvar_evento(evento: EventoConversao):
    """
    Salva o evento no banco Supabase (PostgreSQL),
    utilizando a tabela 'eventos'.
    Aceita tanto eventos com user_id quanto eventos anônimos.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Para campos opcionais: usa getattr, None se não existe
    def _int(val):
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    cursor.execute('''
        INSERT INTO eventos (
            user_id,
            nome,
            sobrenome,
            email,
            telefone,
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
            data_envio
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        _int(getattr(evento, "user_id", None)),
        getattr(evento, "nome", None),
        getattr(evento, "sobrenome", None),
        getattr(evento, "email", None),
        getattr(evento, "telefone", None),
        getattr(evento, "ip", None),
        getattr(evento, "user_agent", None),
        getattr(evento, "url", None),
        getattr(evento, "referrer", None),
        getattr(evento, "pagina_destino", None),
        getattr(evento, "botao_clicado", None),
        getattr(evento, "gclid", None),
        getattr(evento, "fbclid", None),
        getattr(evento, "fbp", None),
        getattr(evento, "fbc", None),
        getattr(evento, "cidade", None),
        getattr(evento, "regiao", None),
        getattr(evento, "pais", None),
        getattr(evento, "campanha", None),
        getattr(evento, "origem", None),
        getattr(evento, "evento", None),
        getattr(evento, "visitor_id", None),
        getattr(evento, "consentimento", None),
        datetime.utcnow()
    ))

    conn.commit()
    conn.close()
