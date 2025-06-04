import sys
import os

# ✅ Adiciona a raiz do projeto ao caminho de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from painel.login import main as login_page

login_page()
