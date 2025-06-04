# utils/caminhos.py
import os

def caminho_user_db():
    return os.path.join(os.path.dirname(__file__), '..', 'database', 'user.db')
