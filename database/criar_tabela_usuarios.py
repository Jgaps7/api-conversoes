import sqlite3

# Conecta ou cria o banco
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Cria a tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nivel TEXT DEFAULT 'comum'
)
""")

# Insere um usuário admin padrão (evita duplicar se já existir)
try:
    cursor.execute("""
    INSERT INTO users (email, senha, nivel)
    VALUES (?, ?, ?)
    """, ("admin@grow.com", "admin123", "admin"))
except sqlite3.IntegrityError:
    print("🟡 Usuário admin já existe.")

conn.commit()
conn.close()
print("✅ Banco de usuários configurado.")
