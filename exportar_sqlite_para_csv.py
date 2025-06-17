import sqlite3
import pandas as pd

# Caminho do banco local
caminho_banco = "users.db"

# Conecta ao banco
conn = sqlite3.connect(caminho_banco)

# Exporta a tabela 'users'
df_users = pd.read_sql("SELECT * FROM users", conn)
df_users.to_csv("users.csv", index=False)
print("✅ Arquivo users.csv exportado com sucesso.")

# Exporta a tabela 'credenciais'
df_credenciais = pd.read_sql("SELECT * FROM credenciais", conn)
df_credenciais.to_csv("credenciais.csv", index=False)
print("✅ Arquivo credenciais.csv exportado com sucesso.")

# Fecha conexão
conn.close()
print("🚀 Exportação concluída.")

