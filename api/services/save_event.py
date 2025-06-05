import sqlite3
from api.event import EventoConversao

def salvar_evento(evento: EventoConversao):
    """
    Salva o evento recebido no banco SQLite (eventos.db),
    com base na estrutura atual da tabela 'eventos'.
    """

    conn = sqlite3.connect("eventos.db")
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
            evento,
            origem
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        evento.evento,
        evento.origem
    ))

    conn.commit()
    conn.close()
