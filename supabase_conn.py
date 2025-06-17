import os
from dotenv import load_dotenv
import psycopg2

# ✅ Carrega variáveis do arquivo .env
load_dotenv()

def get_connection():
    # 🔍 Busca as variáveis de ambiente
    host = os.getenv("SUPABASE_HOST")
    port = os.getenv("SUPABASE_PORT", "5432")  # ✅ fallback seguro
    db = os.getenv("SUPABASE_DB")
    user = os.getenv("SUPABASE_USER")
    pwd = os.getenv("SUPABASE_PASSWORD")

    # ✅ Verificação e debug
    print("🔍 Verificando variáveis de ambiente:")
    print("Host:", host or "❌ Faltando")
    print("Port:", port or "❌ Faltando")
    print("DB:", db or "❌ Faltando")
    print("User:", user or "❌ Faltando")
    print("PWD:", "*" * len(pwd) if pwd else "❌ Faltando")

    # ⚠️ Verifica se alguma variável está faltando
    if not all([host, port, db, user, pwd]):
        raise EnvironmentError("❌ Uma ou mais variáveis do Supabase estão ausentes no .env.")

    # ✅ Conecta ao Supabase PostgreSQL
    return psycopg2.connect(
        host=host,
        dbname=db,
        user=user,
        password=pwd,
        port=int(port)
    )
