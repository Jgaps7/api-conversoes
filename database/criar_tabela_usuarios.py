from supabase_conn import get_connection
import psycopg2
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# Conecta ao banco Supabase
conn = get_connection()
cursor = conn.cursor()

# Cria a tabela de usuários (se não existir)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nivel TEXT NOT NULL DEFAULT 'comum' CHECK (nivel IN ('admin', 'comum'))
);
""")

# Tenta inserir o usuário admin padrão
try:
    cursor.execute("""
    INSERT INTO users (email, senha, nivel)
    VALUES (%s, %s, %s)
    ON CONFLICT (email) DO NOTHING;
    """, ("admin@grow.com", "admin123", "admin"))
    print("✅ Usuário admin criado com sucesso (ou já existia).")
except psycopg2.Error as e:
    print("❌ Erro ao inserir usuário admin:", e)

conn.commit()
conn.close()
print("✅ Banco de usuários configurado.")
