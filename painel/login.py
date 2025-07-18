import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import hashlib
from database import verificar_usuario
from supabase_conn import get_connection

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    st.title("🔐 Painel de Conversões - Grow Solutions")

    # Formulário de login
    with st.form("login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        user = verificar_usuario(email, senha)
        if user:
            st.session_state["autenticado"] = True
            st.session_state["email"] = email
            st.session_state["nivel"] = user[3]  # coluna 'nivel'
            st.session_state["user_id"] = user[0]  # ID do usuário
            st.success("✅ Login realizado com sucesso!")
            st.switch_page("pages/home.py")

        else:
            st.error("❌ Email ou senha inválidos.")

    # 🛠 Se logado e nível for admin, permite cadastrar novos usuários
    if st.session_state.get("autenticado") and st.session_state.get("nivel") == "admin":
        st.markdown("---")
        st.subheader("👤 Criar novo usuário")

        with st.form("form_criar_usuario"):
            novo_email = st.text_input("Novo email")
            nova_senha = st.text_input("Nova senha", type="password")
            novo_nivel = st.selectbox("Nível de acesso", ["admin", "comum"])
            criar = st.form_submit_button("Criar usuário")

        if criar:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email TEXT UNIQUE,
                        senha TEXT,
                        nivel TEXT
                    )
                """)

                cursor.execute("""
                    INSERT INTO users (email, senha, nivel)
                    VALUES (%s, %s, %s)
                    ON CONFLICT(email) DO UPDATE SET senha=excluded.senha, nivel=excluded.nivel
                """, (novo_email, hash_senha(nova_senha), novo_nivel))
                conn.commit()
                conn.close()
                st.success(f"✅ Usuário '{novo_email}' criado ou atualizado com sucesso.")
            except Exception as e:
                st.error(f"Erro ao criar usuário: {str(e)}")
