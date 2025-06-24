from api.event import EventoConversao
from supabase_conn import get_connection  
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
            nome,
            email,
            telefone,
            user_id,
            ip,
            user_agent,
            url_origem,
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
            evento,
            origem,
            visitor_id,
            consentimento
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        evento.nome,
        evento.email,
        evento.telefone,
        evento.user_id,
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
        evento.evento,
        evento.origem,
        evento.visitor_id,
        evento.consentimento
    ))

    conn.commit()
    conn.close()
