import os
import psycopg2
from supabase_conn import get_connection
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# Conecta ao banco Supabase
conn = get_connection()
cursor = conn.cursor()

# Verifica se a tabela 'credenciais' existe
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'credenciais'
    );
""")
tabela_existe = cursor.fetchone()[0]

# Backup se existir
if tabela_existe:
    print("📦 Fazendo backup das credenciais existentes...")
    cursor.execute("SELECT user_id, plataforma, chave, valor FROM credenciais")
    dados_antigos = cursor.fetchall()

    print("🗑️ Removendo tabela antiga...")
    cursor.execute("DROP TABLE credenciais")
else:
    dados_antigos = []
    print("ℹ️ Nenhuma tabela 'credenciais' antiga encontrada. Criando nova...")

# Criação da nova tabela
cursor.execute("""
    CREATE TABLE credenciais (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        plataforma TEXT NOT NULL CHECK (plataforma IN ('google', 'meta')),
        chave TEXT NOT NULL,
        valor TEXT NOT NULL,
        UNIQUE (user_id, plataforma, chave),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
""")
print("✅ Nova tabela 'credenciais' criada com sucesso.")

# Restaura os dados se houver
if dados_antigos:
    print(f"🔁 Regravando {len(dados_antigos)} credenciais anteriores...")
    for user_id, plataforma, chave, valor in dados_antigos:
        cursor.execute("""
            INSERT INTO credenciais (user_id, plataforma, chave, valor)
            VALUES (%s, %s, %s, %s)
        """, (user_id, plataforma, chave, valor))
    print("✅ Dados restaurados com sucesso.")

conn.commit()
conn.close()
print("🏁 Finalizado com sucesso.")
