import sqlite3

# Caminho para o banco de dados
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Criação da tabela de configurações globais (caso não exista)
cursor.execute("""
CREATE TABLE IF NOT EXISTS configuracoes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    envio_ativado INTEGER NOT NULL CHECK (envio_ativado IN (0, 1))
)
""")

# Garante que só existe uma linha com ID = 1
cursor.execute("SELECT COUNT(*) FROM configuracoes WHERE id = 1")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO configuracoes (id, envio_ativado) VALUES (1, 0)")
    print("🔧 Flag de envio inicializada como DESATIVADA.")

conn.commit()
conn.close()
print("✅ Tabela 'configuracoes' criada com sucesso.")
