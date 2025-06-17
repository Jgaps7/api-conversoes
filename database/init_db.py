from supabase_conn import get_connection
import psycopg2
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# Conecta ao banco PostgreSQL (Supabase)
conn = get_connection()
cursor = conn.cursor()

# Criação da tabela 'eventos'
cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    
    -- Identificação do lead
    nome TEXT,
    email TEXT,
    telefone TEXT,
    user_id TEXT,

    -- Dados técnicos
    ip TEXT,
    user_agent TEXT,
    url_origem TEXT,
    referrer TEXT,
    pagina_destino TEXT,
    botao_clicado TEXT,

    -- Cookies primários
    gclid TEXT,
    fbclid TEXT,
    fbp TEXT,
    fbc TEXT,

    -- Localização
    cidade TEXT,
    regiao TEXT,
    pais TEXT,

    -- Evento e origem
    evento TEXT NOT NULL,
    origem TEXT NOT NULL, -- google | meta
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Consentimento e status de envio
    consentimento TEXT DEFAULT 'não informado',
    enviado_google BOOLEAN DEFAULT FALSE,
    enviado_meta BOOLEAN DEFAULT FALSE
);
""")

conn.commit()
conn.close()
print("✅ Tabela 'eventos' criada com sucesso no PostgreSQL.")
