import sys
import os
import streamlit as st
from painel.login import main as login_page

st.set_page_config(page_title="Login Grow", page_icon="🔐", layout="centered")

# ✅ Garante que a raiz do projeto esteja no sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ✅ Protege a página de login: se o usuário já estiver logado, bloqueia acesso
if st.session_state.get("autenticado"):
    st.warning("Você já está logado.")
    st.stop()

# ✅ Oculta visualmente o link desta página do menu lateral (opcional)
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] li:first-child {display: none;}
    </style>
""", unsafe_allow_html=True)

# ✅ Executa a tela de login normalmente
login_page()
