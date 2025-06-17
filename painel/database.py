import hashlib
from supabase_conn import get_connection
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def hash_senha(senha: str) -> str:
    """
    Retorna o hash SHA-256 da senha fornecida.
    """
    return hashlib.sha256(senha.strip().encode()).hexdigest()

def verificar_usuario(email: str, senha: str):
    """
    Verifica se o email e a senha (em hash) existem na base de usuários.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        senha_hash = hash_senha(senha)
        cursor.execute("SELECT * FROM users WHERE email = %s AND senha = %s", (email, senha_hash))
        user = cursor.fetchone()
        return user
    finally:
        conn.close()
