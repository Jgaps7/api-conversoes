from supabase_conn import get_connection
import psycopg2
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# Conecta ao banco Supabase
conn = get_connection()
cursor = conn.cursor()

# Criação da tabela de configurações globais
cursor.execute("""
CREATE TABLE IF NOT EXISTS configuracoes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    envio_ativado BOOLEAN NOT NULL
);
""")

# Verifica se já existe a linha única com id = 1
cursor.execute("SELECT COUNT(*) FROM configuracoes WHERE id = 1")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO configuracoes (id, envio_ativado)
        VALUES (1, FALSE)
    """)
    print("🔧 Flag de envio inicializada como DESATIVADA.")
else:
    print("ℹ️ Flag de envio já configurada.")

conn.commit()
conn.close()
print("✅ Tabela 'configuracoes' criada com sucesso.")
