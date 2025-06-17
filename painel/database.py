from supabase_conn import get_connection
import hashlib

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.strip().encode()).hexdigest()

def verificar_usuario(email: str, senha: str):
    conn = None  # <- importante para evitar UnboundLocalError
    try:
        conn = get_connection()
        cursor = conn.cursor()
        senha_hash = hash_senha(senha)
        cursor.execute("SELECT * FROM users WHERE email = %s AND senha = %s", (email, senha_hash))
        return cursor.fetchone()
    finally:
        if conn:
            conn.close()
