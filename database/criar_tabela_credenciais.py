from supabase_conn import get_connection
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Conecta ao Supabase (PostgreSQL)
conn = get_connection()
cursor = conn.cursor()

# Criação da tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nivel TEXT NOT NULL CHECK (nivel IN ('admin', 'comum'))
);
""")

print("✅ Tabela 'users' criada com sucesso.")

conn.commit()
conn.close()