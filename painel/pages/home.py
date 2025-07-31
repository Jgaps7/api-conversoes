import os
import sys
import json
import asyncio
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from auth import requer_login

# Ajuste de path para importar do projeto
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from api.event import EventoConversao
from api.services.google import enviar_para_google
from api.services.meta import enviar_para_meta
from supabase_conn import get_connection

requer_login()

# --------------------- CONFIGURAÇÃO ---------------------
st.set_page_config(page_title="Painel de Conversões GROW", page_icon="📊", layout="wide")

with st.sidebar:
    if st.session_state.get("autenticado"):
        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.success("Logout realizado com sucesso.")
            st.rerun()


# --------------------- CSS GLOBAL ---------------------
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f9f9f9;
        }
        .header {
            background-color: #2b303a;
            padding: 1rem 2rem;
            border-radius: 10px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo {
            font-size: 1.4rem;
            font-weight: bold;
            color: #f8c100;
        }
        .botao-sair {
            background-color: #f04e4e;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        .botao-sair:hover {
            background-color: #d63a3a;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------- BANCO DE DADOS ---------------------
@st.cache_data(show_spinner=False)
def carregar_eventos():
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM eventos", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar eventos: {e}")
        return pd.DataFrame()

df = carregar_eventos()
print("🧪 Colunas carregadas:", df.columns.tolist())

# 🔹 Normaliza/garante colunas básicas mesmo para eventos anônimos:
if "email" not in df.columns:
    df["email"] = "Anônimo"
df["email"] = df["email"].fillna("Anônimo")  # Pode vir NaN/null

if "url_origem" not in df.columns:
    if "url" in df.columns:
        df["url_origem"] = df["url"]
    else:
        df["url_origem"] = "desconhecido"

if "campanha" not in df.columns:
    df["campanha"] = "Indefinida"

# Se quiser filtrar só pelo user_id do cliente logado:
if st.session_state["nivel"] != "admin":
    df = df[df["user_id"] == st.session_state["user_id"]]

# Filtros universais
clientes = ["Todos"] + list(df["email"].unique())
dominios = ["Todos"] + list(df["url_origem"].unique())
campanhas = ["Todas"] + list(df["campanha"].unique())

email_cliente = st.sidebar.selectbox("👤 Cliente (email)", options=clientes)
dominio = st.sidebar.selectbox("🌐 Domínio", options=dominios)
campanha = st.sidebar.selectbox("📣 Campanha", options=campanhas)

df["data_envio"] = pd.to_datetime(df.get("data_envio", df.get("data_hora", datetime.now())), errors="coerce")
if df["data_envio"].notna().any():
    data_min = df["data_envio"].min().date()
    data_max = df["data_envio"].max().date()
else:
    hoje = datetime.today().date()
    data_min = data_max = hoje

data_inicio = st.sidebar.date_input("📅 Data Início", value=data_min, min_value=data_min, max_value=data_max)
data_fim = st.sidebar.date_input("📅 Data Fim", value=data_max, min_value=data_min, max_value=data_max)

# Filtro universal
filtro = (df["data_envio"].dt.date >= data_inicio) & (df["data_envio"].dt.date <= data_fim)
if email_cliente != "Todos":
    filtro &= (df["email"] == email_cliente)
if dominio != "Todos":
    filtro &= (df["url_origem"] == dominio)
if campanha != "Todas":
    filtro &= (df["campanha"] == campanha)

df_filtrado = df[filtro]



# ---------------- DESTAQUE DE CAMPANHA ----------------
if "campanha" in df_filtrado.columns and not df_filtrado.empty:
    campanhas_ativas = df_filtrado["campanha"].dropna().unique()
    if len(campanhas_ativas) == 1:
        st.info(f"📣 Campanha Ativa: **{campanhas_ativas[0]}**")
    elif len(campanhas_ativas) > 1:
        st.info(f"📣 Campanhas Ativas: {', '.join(campanhas_ativas)}")


if df_filtrado.empty:
    st.warning("Nenhum evento encontrado com os filtros selecionados.")
    st.stop()

# --------------------- CABEÇALHO VISUAL ---------------------
st.markdown(f"""
    <div class="header">
        <div class="logo">🚀 Grow Solutions - Painel de Conversões</div>
        <div>Cliente: <b>{email_cliente}</b></div>
        <form action="/logout" method="get">
            <button class="botao-sair">Sair</button>
        </form>
    </div>
    <br>
""", unsafe_allow_html=True)

if "email" in st.session_state:
    st.markdown(f"**Usuário logado:** {st.session_state['email']}")

# --------------------- MENU LATERAL ---------------------
menu = st.sidebar.radio("Navegação", ["📊 Dashboard", "⚙️ Logs e Falhas", "🧾 Reenviados", "🔐 Credenciais"])

# --------------------- LOGS ---------------------
def carregar_logs(caminho_log):
    if not os.path.exists(caminho_log):
        return []
    with open(caminho_log, "r", encoding="utf-8") as f:
        return [json.loads(linha.strip()) for linha in f.readlines()]

# --------------------- TELAS ---------------------

def mostrar_dashboard(df_filtrado):
    # 🔹 Ações rápidas adicionadas para dar mais controle ao usuário
    st.subheader("⚡ Ações Rápidas")
    col1, col2, col3 = st.columns(3)

    # 🔁 Reenviar eventos com falha (automatizado em lote)
    with col1:
        if st.button("🔁 Reenviar eventos com falha", use_container_width=True):
            erro_google = carregar_logs("logs/erro_google.log")
            erro_meta = carregar_logs("logs/erro_meta.log")
            falhas = erro_google + erro_meta
            if not falhas:
                st.success("Nenhuma falha encontrada para reenviar.")
            else:
                total = 0
                for falha in falhas:
                    evento = EventoConversao(
                        email=None, telefone=None, nome=None, user_id=None,
                        ip=None, user_agent=None, url=None, referrer=None,
                        pagina_destino=None, botao_clicado=None,
                        gclid=falha.get("gclid"), fbclid=falha.get("fbclid"),
                        fbp=None, fbc=None, cidade=None, regiao=None, pais=None,
                        origem="google" if falha.get("gclid") else "meta",
                        evento=falha.get("evento", "lead")
                    )
                    # Chamada assíncrona conforme origem
                    if evento.origem == "google":
                        asyncio.run(enviar_para_google(evento))
                    else:
                        asyncio.run(enviar_para_meta(evento))
                    total += 1
                st.success(f"✅ {total} eventos reenviados com sucesso!")

    # 📥 Exportar CSV com os dados filtrados
    with col2:
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar CSV", data=csv, file_name="eventos_filtrados.csv", mime="text/csv", use_container_width=True)

    # 🔄 Atualiza a interface
    with col3:
        if st.button("🔄 Atualizar painel", use_container_width=True):
            st.experimental_rerun()

    st.divider()
    st.subheader("📈 Resumo Geral")

    # 🔸 KPIs principais
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Eventos", len(df_filtrado))
    col2.metric("Google", df_filtrado[df_filtrado['origem'] == 'google'].shape[0])
    col3.metric("Meta", df_filtrado[df_filtrado['origem'] == 'meta'].shape[0])

    st.divider()
    st.subheader("Distribuição por Origem dos Eventos")

    # 📊 Gráfico por origem
    fig1 = px.histogram(df_filtrado, x="origem", color="origem", title="Eventos por Origem")
    st.plotly_chart(fig1, use_container_width=True)

    # 📊 Gráfico por tipo de evento
    if "evento" in df_filtrado.columns:
        st.subheader("Eventos por Tipo")
        fig2 = px.histogram(df_filtrado, x="evento", color="origem", title="Distribuição por Tipo de Evento")
        st.plotly_chart(fig2, use_container_width=True)

    # 📊 Novo: Distribuição por campanha
    if "campanha" in df_filtrado.columns:
        st.subheader("Campanhas Ativadas")
        fig3 = px.histogram(
            df_filtrado,
            x="campanha",
            color="origem",
            title="Eventos por Campanha",
            barmode="group"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # 🕒 Tabela com os últimos registros
    st.subheader("🕒 Últimos Eventos Registrados")
    st.dataframe(df_filtrado.sort_values(by="id", ascending=False).head(10), use_container_width=True)

    st.divider()
    st.subheader("📊 Eventos por Dia")

    # ✅ Novo gráfico: Eventos por data (ETAPA 2.2)
    if "data_envio" in df_filtrado.columns:
        df_filtrado["data_envio_dia"] = df_filtrado["data_envio"].dt.date
        
        fig_dia = px.histogram(
            df_filtrado,
            x="data_envio_dia",
            color="origem",
            title="Quantidade de eventos por dia",
            nbins=30,
            labels={"data_envio_dia": "Data"}
        )
        st.plotly_chart(fig_dia, use_container_width=True)

        # 🔍 Eventos por dia por campanha
        if "campanha" in df_filtrado.columns:
            fig_camp_dia = px.histogram(
                df_filtrado,
                x="data_envio_dia",
                color="campanha",
                title="Eventos por Dia por Campanha",
                barmode="group"
            )
            st.plotly_chart(fig_camp_dia, use_container_width=True)
    else:
        st.info("Coluna 'data_envio' não encontrada.")

    st.divider()
    st.subheader("🔁 Reenvios por Status")

    # ✅ Novo gráfico: Sucesso vs Falha nos reenvios (ETAPA 2.2)
    falhas = carregar_logs("logs/erro_google.log") + carregar_logs("logs/erro_meta.log")
    sucesso = carregar_logs("logs/reenviados.log")

    df_status = pd.DataFrame({
        "Status": ["Sucesso", "Falha"],
        "Quantidade": [len(sucesso), len(falhas)]
    })

    fig_status = px.pie(df_status, names="Status", values="Quantidade", title="Status dos Reenvios")
    st.plotly_chart(fig_status, use_container_width=True)

     # === [NOVO BLOCO: ANÁLISE DE EVENTOS ANÔNIMOS] ===
    st.divider()
    st.subheader("🕵️‍♂️ Eventos Anônimos (Cookies/Site)")

    # Filtra só eventos anônimos (cookies ou site)
    df_anonimos = df_filtrado[df_filtrado["origem"].isin(["cookies", "site"])]

    # Exibe tabela resumida
    st.markdown("**Total de eventos anônimos:** {}".format(len(df_anonimos)))
    if not df_anonimos.empty:
        # Tabela de eventos anônimos
        st.dataframe(
            df_anonimos.sort_values(by="data_envio", ascending=False).head(10),
            use_container_width=True,
            height=320
        )

        # Gráfico por tipo de evento anônimo
        fig_anon = px.histogram(
            df_anonimos,
            x="evento",
            color="origem",
            title="Eventos Anônimos por Tipo"
        )
        st.plotly_chart(fig_anon, use_container_width=True)
    else:
        st.info("Nenhum evento anônimo registrado até o momento.")


def mostrar_logs():
    # 🔍 Lista de falhas individuais (mantido igual)
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
                        email=None, telefone=None, nome=None, user_id=None, 
                        ip=None, user_agent=None, url=None, referrer=None,
                        pagina_destino=None, botao_clicado=None,
                        gclid=falha.get("gclid"), fbclid=falha.get("fbclid"),
                        fbp=None, fbc=None, cidade=None, regiao=None, pais=None,
                        origem="google" if falha.get("gclid") else "meta",
                        evento=falha.get("evento", "lead")
                    )
                    if evento.origem == "google":
                        resposta = asyncio.run(enviar_para_google(evento))
                    else:
                        resposta = asyncio.run(enviar_para_meta(evento))
                    st.success(f"✅ Reenvio realizado com sucesso: {resposta}")


def mostrar_reenviados():
    # 📤 Reenvios registrados com sucesso (mantido igual)
    st.subheader("📤 Eventos Reenviados com Sucesso")
    reenviados = carregar_logs("logs/reenviados.log")
    if not reenviados:
        st.info("Nenhum evento foi reenviado ainda.")
    else:
        df_re = pd.DataFrame(reenviados)
        st.dataframe(df_re.sort_values(by="evento", ascending=False).head(10), use_container_width=True)


def mostrar_credenciais(email_cliente):
    st.subheader("🔐 Cadastro de Credenciais por Plataforma")

    # ✅ Alteração: banco certo agora é 'users.db' (não 'eventos.db')
    conn = get_connection()
    cursor = conn.cursor()

    # Lista todos os usuários e permite selecionar o cliente
    usuarios = pd.read_sql_query("SELECT id, email FROM users", conn)
    selecionado = st.selectbox("👤 Selecione o cliente", usuarios["email"].tolist())
    
    # Recupera o user_id com base no email selecionado
    user_id = usuarios[usuarios["email"] == selecionado]["id"].values[0]

    # ✅ Campos dinâmicos por plataforma
    campos_por_plataforma = {
        "google": ["developer_token", "client_id", "client_secret", "refresh_token", "login_customer_id"],
        "meta": ["access_token", "pixel_id", "app_id", "app_secret"]
    }

    plataforma = st.selectbox("Plataforma", ["google", "meta"])
    chaves = campos_por_plataforma[plataforma]

    # Formulário dinâmico com todos os campos da plataforma escolhida
    with st.form("form_credenciais_dinamico"):
        st.markdown("**Preencha os dados abaixo para salvar suas credenciais:**")
        valores = {}
        for chave in chaves:
            valores[chave] = st.text_input(f"{chave}", type="password")

        submitted = st.form_submit_button("💾 Salvar todas credenciais")
        if submitted:
            for chave, valor in valores.items():
                if valor.strip():
                    cursor.execute("""
                        INSERT INTO credenciais (user_id, plataforma, chave, valor)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT(user_id, plataforma, chave) DO UPDATE SET valor = excluded.valor
                    """, (user_id, plataforma, chave, valor))
            conn.commit()
            st.success(f"✅ Credenciais salvas com sucesso para {selecionado} – plataforma {plataforma}")

   

# ------------------ EDIÇÃO INLINE DAS CREDENCIAIS ------------------
st.divider()
st.subheader("✏️ Editar Credenciais Existentes")

with get_connection() as conn:
    cursor = conn.cursor()

    # Busca user_id pela tabela users
    cursor.execute("SELECT id FROM users WHERE email = %s", (email_cliente,))
    user = cursor.fetchone()
    if not user:
        st.error("Usuário não encontrado na tabela 'users'.")
        st.stop()

    user_id = user[0]

    df_edit = pd.read_sql_query("""
        SELECT id, plataforma, chave, valor
        FROM credenciais
        WHERE user_id = %s
    """, conn, params=(user_id,))

    if df_edit.empty:
        st.info("Nenhuma credencial cadastrada ainda.")
    else:
        for index, row in df_edit.iterrows():
            with st.expander(f"{row['plataforma'].upper()} – {row['chave']}"):
                novo_valor = st.text_input(
                    f"Novo valor para {row['chave']}",
                    type="password",
                    key=f"editar_{row['id']}"
                )
                if st.button("💾 Salvar alteração", key=f"salvar_{row['id']}"):
                    cursor.execute("""
                        UPDATE credenciais
                        SET valor = %s
                        WHERE id = %s
                    """, (novo_valor, row['id']))
                    conn.commit()
                    st.success("Credencial atualizada com sucesso.")

    # Formulário para nova credencial
    with st.form("form_credenciais"):
        plataforma = st.selectbox("Plataforma", ["google", "meta"])
        chave = st.text_input("Nome da chave")
        valor = st.text_input("Valor", type="password")
        submit = st.form_submit_button("💾 Salvar credencial")

        if submit:
            cursor.execute("""
                INSERT INTO credenciais (user_id, plataforma, chave, valor)
                VALUES (%s, %s, %s, %s)
            """, (user_id, plataforma, chave, valor))
            conn.commit()
            st.success(f"Credencial '{chave}' salva com sucesso para {plataforma}!")

    # Exibe credenciais cadastradas
    st.divider()
    st.subheader("🔎 Credenciais Cadastradas")

    df_cred = pd.read_sql_query("""
        SELECT plataforma, chave, '************' AS valor
        FROM credenciais
        WHERE user_id = %s
    """, conn, params=(user_id,))
    st.dataframe(df_cred, use_container_width=True)

# --------------------- EXIBIÇÃO CONDICIONAL ---------------------
if menu == "📊 Dashboard":
    mostrar_dashboard(df_filtrado)
elif menu == "⚙️ Logs e Falhas":
    mostrar_logs()
elif menu == "🧾 Reenviados":
    mostrar_reenviados()
elif menu == "🔐 Credenciais":
    mostrar_credenciais(email_cliente)