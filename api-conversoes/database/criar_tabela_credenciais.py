import sqlite3

# Caminho do banco
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Criação da tabela de credenciais multiusuário
cursor.execute("""
CREATE TABLE IF NOT EXISTS credenciais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plataforma TEXT NOT NULL CHECK(plataforma IN ('google', 'meta')),
    chave TEXT NOT NULL,
    valor TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("✅ Tabela 'credenciais' criada com sucesso.")
