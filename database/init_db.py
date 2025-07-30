from supabase_conn import get_connection
import psycopg2
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,

    -- Identificação do lead
    nome TEXT,
    sobrenome TEXT,
    email TEXT,
    telefone TEXT,
    user_id TEXT,

    -- Dados técnicos
    ip TEXT,
    user_agent TEXT,
    url TEXT,
    referrer TEXT,
    pagina_destino TEXT,
    botao_clicado TEXT,

    -- Cookies primários e rastreamento
    gclid TEXT,
    fbclid TEXT,
    fbp TEXT,
    fbc TEXT,
    click_id TEXT,
    visitor_id TEXT,

    -- Localização
    cidade TEXT,
    regiao TEXT,
    pais TEXT,

    -- UTM
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,

    -- Evento e origem
    evento TEXT NOT NULL,
    origem TEXT NOT NULL, -- google | meta | cookies | site
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_envio TIMESTAMP,

    -- Consentimento e status de envio
    consentimento BOOLEAN DEFAULT FALSE,
    enviado_google BOOLEAN DEFAULT FALSE,
    enviado_meta BOOLEAN DEFAULT FALSE
);
""")

conn.commit()
conn.close()
print("✅ Tabela 'eventos' criada/atualizada com sucesso no PostgreSQL.")
