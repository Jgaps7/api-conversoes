import streamlit as st

def requer_login():
    """
    Verifica se o usuário está logado. Caso contrário, bloqueia a página.
    """
    if not st.session_state.get("autenticado"):
        st.error("⛔ Acesso não autorizado. Faça login primeiro.")
        st.stop()
