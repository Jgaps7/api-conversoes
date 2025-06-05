import sqlite3
import os

# Caminho relativo para o banco, saindo de /database para a raiz
db_path = os.path.join(os.path.dirname(__file__), "..", "users.db")
db_path = os.path.abspath(db_path)

print(f"🔗 Conectando ao banco: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verifica se a tabela 'credenciais' existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credenciais'")
tabela_existe = cursor.fetchone()

if tabela_existe:
    print("📦 Fazendo backup das credenciais existentes...")
    cursor.execute("SELECT user_id, plataforma, chave, valor FROM credenciais")
    dados_antigos = cursor.fetchall()

    print("🗑️ Removendo tabela antiga...")
    cursor.execute("DROP TABLE credenciais")
else:
    dados_antigos = []
    print("ℹ️ Nenhuma tabela 'credenciais' antiga encontrada. Criando nova...")

# Criação da nova tabela com UNIQUE e FOREIGN KEY
cursor.execute("""
CREATE TABLE credenciais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plataforma TEXT NOT NULL CHECK(plataforma IN ('google', 'meta')),
    chave TEXT NOT NULL,
    valor TEXT NOT NULL,
    UNIQUE(user_id, plataforma, chave),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
print("✅ Nova tabela 'credenciais' criada com sucesso.")

# Restaura os dados (se houver)
if dados_antigos:
    print(f"🔁 Regravando {len(dados_antigos)} credenciais anteriores...")
    for user_id, plataforma, chave, valor in dados_antigos:
        cursor.execute("""
            INSERT INTO credenciais (user_id, plataforma, chave, valor)
            VALUES (?, ?, ?, ?)
        """, (user_id, plataforma, chave, valor))
    print("✅ Dados restaurados com sucesso.")

conn.commit()
conn.close()
print("🏁 Finalizado com sucesso.")
