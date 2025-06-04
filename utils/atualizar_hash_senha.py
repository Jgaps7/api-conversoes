import sqlite3
import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Acesse o banco
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Atualize a senha do admin para o hash
senha_clara = "admin123"
senha_hash = hash_senha(senha_clara)

cursor.execute("""
    UPDATE users
    SET senha = ?
    WHERE email = 'admin@grow.com'
""", (senha_hash,))

conn.commit()
conn.close()

print("✅ Senha do admin atualizada com hash SHA-256.")
