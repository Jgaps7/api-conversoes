import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_connection():
    host = os.getenv("SUPABASE_HOST")
    port = os.getenv("SUPABASE_PORT")
    db = os.getenv("SUPABASE_DB")
    user = os.getenv("SUPABASE_USER")
    pwd = os.getenv("SUPABASE_PASSWORD")

    print("🔍 Verificando variáveis:")
    print("Host:", host)
    print("Port:", port)
    print("DB:", db)
    print("User:", user)
    print("PWD:", "*" * len(pwd) if pwd else "None")

    return psycopg2.connect(
        host=host,
        dbname=db,
        user=user,
        password=pwd,
        port=int(port)
    )
