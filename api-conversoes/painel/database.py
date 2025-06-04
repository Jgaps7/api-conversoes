import sqlite3
import hashlib
import os

# Caminho seguro para o banco, mesmo em execuções de subpastas
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "users.db")

def conectar():
    return sqlite3.connect(DB_PATH)

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
        conn = conectar()
        cursor = conn.cursor()
        senha_hash = hash_senha(senha)
        cursor.execute("SELECT * FROM users WHERE email = ? AND senha = ?", (email, senha_hash))
        user = cursor.fetchone()
        return user
    finally:
        conn.close()
