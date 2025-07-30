import os
import json
import asyncio
import pandas as pd
import streamlit as st
import plotly.express as px
import sys

# Ajuste do path para importar corretamente
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from api.event import EventoConversao
from api.services.google import enviar_para_google
from api.services.meta import enviar_para_meta
from painel.auth import requer_login
from supabase_conn import get_connection

requer_login()

# --------------------- CONFIGURAÇÃO ---------------------
st.set_page_config(page_title="Painel de Conversões", page_icon="📊", layout="wide")
st.title("📊 Painel de Monitoramento de Eventos")

# Botão de logout
with st.sidebar:
    if st.session_state.get("autenticado"):
        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.success("Logout realizado com sucesso.")
            st.rerun()

# Proteção
if not st.session_state.get("autenticado"):
    st.error("⛔ Acesso não autorizado. Faça login primeiro.")
    st.stop()

# --------------------- BANCO DE DADOS ---------------------
@st.cache_data(show_spinner=False)
def carregar_eventos():
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM eventos", conn)
        conn.close()
        # Só faz expansão se a coluna 'dados' existir
        if "dados" in df.columns:
            df['dados'] = df['dados'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
            dados_expandido = pd.json_normalize(df['dados'])
            df = df.drop(columns=['dados']).join(dados_expandido)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar eventos: {e}")
        return pd.DataFrame()
    
# --------------------- TRATAR JSON DADOS DINÂMICOS ---------------------
if "dados" in df.columns:
    # Converte JSON string para dict
    df['dados'] = df['dados'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    # Expande todos os campos extras em colunas
    df_dados = pd.json_normalize(df['dados'])
    # Concatena ao dataframe principal (colunas duplicadas serão renomeadas com _x)
    df = pd.concat([df.drop(columns=['dados']), df_dados], axis=1)

# --------------------- GRÁFICOS E MÉTRICAS ---------------------
st.subheader("📈 Resumo Geral")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Eventos", len(df))
col2.metric("Google", df[df['origem'] == 'google'].shape[0])
col3.metric("Meta", df[df['origem'] == 'meta'].shape[0])

st.divider()

# Gráfico por origem
st.subheader("Distribuição por Origem dos Eventos")
fig1 = px.histogram(df, x="origem", color="origem", title="Eventos por Origem")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico por tipo de evento
if "evento" in df.columns:
    st.subheader("Eventos por Tipo")
    fig2 = px.histogram(df, x="evento", color="origem", title="Distribuição por Tipo de Evento")
    st.plotly_chart(fig2, use_container_width=True)

# Últimos eventos
st.subheader("🕒 Últimos Eventos Registrados")
st.dataframe(df.sort_values(by="id", ascending=False).head(10), use_container_width=True)

st.divider()

# --------------------- LOGS DE ERRO ---------------------
def carregar_logs(caminho_log):
    if not os.path.exists(caminho_log):
        return []
    with open(caminho_log, "r", encoding="utf-8") as f:
        return [json.loads(linha.strip()) for linha in f.readlines()]

st.subheader("❌ Eventos com Falha de Envio")

erro_google = carregar_logs("logs/erro_google.log")
erro_meta = carregar_logs("logs/erro_meta.log")
falhas = erro_google + erro_meta

if not falhas:
    st.success("Nenhuma falha de envio registrada nos logs.")
else:
    for i, falha in enumerate(falhas):
        with st.expander(f"Falha {i+1} - Origem: {falha.get('origem', 'desconhecida').upper()} | Evento: {falha.get('evento')}"):
            st.json(falha)

            if st.button(f"🔁 Reenviar Evento {i+1}"):
                evento = EventoConversao(
                    email=None,
                    telefone=None,
                    nome=None,
                    user_id=None,
                    ip=None,
                    user_agent=None,
                    url=None,
                    referrer=None,
                    pagina_destino=None,
                    botao_clicado=None,
                    gclid=falha.get("gclid"),
                    fbclid=falha.get("fbclid"),
                    fbp=None,
                    fbc=None,
                    cidade=None,
                    regiao=None,
                    pais=None,
                    origem="google" if falha.get("gclid") else "meta",
                    evento=falha.get("evento", "lead")
                )

                if evento.origem == "google":
                    resposta = asyncio.run(enviar_para_google(evento))
                else:
                    resposta = asyncio.run(enviar_para_meta(evento))

                st.success(f"✅ Reenvio realizado com sucesso: {resposta}")
