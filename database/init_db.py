import sqlite3

# Conecta (ou cria) o banco de dados
conn = sqlite3.connect("eventos.db")
cursor = conn.cursor()

# Cria ou atualiza a tabela de eventos com todos os campos necessários
cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
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
    enviado_google INTEGER DEFAULT 0,
    enviado_meta INTEGER DEFAULT 0
)
""")

# Confirma e fecha conexão
conn.commit()
conn.close()
