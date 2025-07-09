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
    """

    conn = get_connection()
    cursor = conn.cursor()

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
        int(evento.user_id) if evento.user_id else None,
        evento.nome,
        evento.sobrenome,
        evento.email,
        evento.telefone,
        evento.ip,
        evento.user_agent,
        evento.url,
        evento.referrer,
        evento.pagina_destino,
        evento.botao_clicado,
        evento.gclid,
        evento.fbclid,
        evento.fbp,
        evento.fbc,
        evento.cidade,
        evento.regiao,
        evento.pais,
        evento.campanha,
        evento.origem,
        evento.evento,
        evento.visitor_id,
        evento.consentimento,
        datetime.utcnow()
    ))

    conn.commit()
    conn.close()
