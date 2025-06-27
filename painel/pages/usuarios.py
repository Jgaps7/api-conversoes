import streamlit as st
import hashlib
import pandas as pd
from supabase_conn import get_connection
from auth import requer_login
from utils.config import get_envio_ativado, set_envio_ativado
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


requer_login()


# 🚫 Proteção: só administradores acessam
if not st.session_state.get("autenticado"):
    st.error("⛔ Acesso não autorizado. Faça login primeiro.")
    st.stop()

if st.session_state.get("nivel") != "admin":
    st.error("⛔ Acesso restrito a administradores.")
    st.stop()

with st.sidebar:
    if st.session_state.get("autenticado"):
        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.success("Logout realizado com sucesso.")
            st.rerun()


# Conecta ao banco
conn = get_connection()
cursor = conn.cursor()

# Função para hashear senhas
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

st.title("👥 Gerenciar Usuários e Credenciais")

# Lista de usuários
df_usuarios = pd.read_sql_query("SELECT id, email, nivel FROM users", conn)
st.subheader("📋 Lista de Usuários Cadastrados")
st.dataframe(df_usuarios, use_container_width=True)

# Cadastro
st.subheader("➕ Cadastrar Novo Usuário")
with st.form("form_cadastro"):
    novo_email = st.text_input("Email")
    nova_senha = st.text_input("Senha", type="password")
    novo_nivel = st.selectbox("Nível de Acesso", ["admin", "comum"])
    cadastrar = st.form_submit_button("Cadastrar")

    if cadastrar:
        try:
            cursor.execute("SELECT 1 FROM users WHERE email = %s", (novo_email,))
            if cursor.fetchone():
                st.error("❌ Este e-mail já está cadastrado.")
            else:
                cursor.execute("""
                    INSERT INTO users (email, senha, nivel)
                    VALUES (%s, %s, %s)
                """, (novo_email, hash_senha(nova_senha), novo_nivel))
                conn.commit()
                st.success(f"✅ Usuário '{novo_email}' cadastrado com sucesso!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao cadastrar usuário: {str(e)}")


# Edição/Remoção    
st.subheader("✏️ Editar ou ❌ Remover Usuários e Gerenciar Credenciais")
for _, usuario in df_usuarios.iterrows():
    with st.expander(f"👤 {usuario['email']}"):
        novo_nivel = st.selectbox(
            "Nível", ["admin", "comum"],
            index=0 if usuario["nivel"] == "admin" else 1,
            key=f"nivel_{usuario['id']}"
        )

        nova_senha = st.text_input("Nova senha (opcional)", type="password", key=f"senha_{usuario['id']}")
        col1, col2 = st.columns(2)

        if col1.button("Salvar alterações", key=f"salvar_{usuario['id']}"):
            try:
                if nova_senha.strip():
                    cursor.execute(
                        "UPDATE users SET senha = %s, nivel = %s WHERE id = %s",
                        (hash_senha(nova_senha.strip()), novo_nivel, usuario["id"])
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET nivel = %s WHERE id = %s",
                        (novo_nivel, usuario["id"])
                    )
                conn.commit()
                st.success("Usuário atualizado com sucesso.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar usuário: {str(e)}")

        if col2.button("❌ Remover usuário", key=f"remover_{usuario['id']}"):
            try:
                cursor.execute("DELETE FROM users WHERE id = %s", (usuario["id"],))
                conn.commit()
                st.warning("Usuário removido.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao remover usuário: {str(e)}")

        # 📌 Credenciais da Meta Ads
        st.markdown("**🔵 Credenciais Meta Ads**")
        cursor.execute("""
            SELECT chave, valor FROM credenciais
            WHERE user_id = %s AND plataforma = 'meta'
        """, (usuario["id"],))
        credenciais_meta = {row[0]: row[1] for row in cursor.fetchall()}

        meta_pixel_id_valor = "************" if "PIXEL_ID" in credenciais_meta else ""
        meta_token_valor = "************" if "ACCESS_TOKEN" in credenciais_meta else ""

        meta_pixel_id = st.text_input("PIXEL_ID", value=meta_pixel_id_valor, key=f"meta_pixel_{usuario['id']}")
        meta_token = st.text_input("ACCESS_TOKEN", value=meta_token_valor, key=f"meta_token_{usuario['id']}")

        if st.button("💾 Salvar credenciais Meta", key=f"meta_save_{usuario['id']}"):
            if not meta_pixel_id.strip() or not meta_token.strip():
                st.error("❌ Preencha todos os campos antes de salvar.")
            else:
                try:
                    if meta_pixel_id != "************":
                        cursor.execute("""
                            INSERT INTO credenciais (user_id, plataforma, chave, valor)
                            VALUES (%s, 'meta', 'PIXEL_ID', %s)
                            ON CONFLICT(user_id, plataforma, chave) DO UPDATE SET valor = excluded.valor
                        """, (usuario["id"], meta_pixel_id.strip()))

                    if meta_token != "************":
                        cursor.execute("""
                            INSERT INTO credenciais (user_id, plataforma, chave, valor)
                            VALUES (%s, 'meta', 'ACCESS_TOKEN', %s)
                            ON CONFLICT(user_id, plataforma, chave) DO UPDATE SET valor = excluded.valor
                        """, (usuario["id"], meta_token.strip()))

                    conn.commit()
                    st.success("✅ Credenciais da Meta salvas com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar credenciais: {str(e)}")

    # 📌 Credenciais do Google Ads
        st.markdown("**🟢 Credenciais Google Ads**")
        cursor.execute("""
            SELECT chave, valor FROM credenciais
            WHERE user_id = %s AND plataforma = 'google'
        """, (usuario["id"],))
        credenciais_google_existentes = {row[0]: row[1] for row in cursor.fetchall()}

        google_client_id = st.text_input("CLIENT_ID",
            value="************" if "CLIENT_ID" in credenciais_google_existentes else "",
            key=f"google_client_{usuario['id']}"
        )
        google_refresh_token = st.text_input("REFRESH_TOKEN",
            value="************" if "REFRESH_TOKEN" in credenciais_google_existentes else "",
            key=f"google_refresh_{usuario['id']}"
        )
        google_dev_token = st.text_input("DEVELOPER_TOKEN",
            value="************" if "DEVELOPER_TOKEN" in credenciais_google_existentes else "",
            key=f"google_dev_{usuario['id']}"
        )
        google_cust_id = st.text_input("CUSTOMER_ID",
            value="************" if "CUSTOMER_ID" in credenciais_google_existentes else "",
            key=f"google_cust_{usuario['id']}"
        )
        google_conv_action_id = st.text_input("CONVERSION_ACTION_ID",
            value="************" if "CONVERSION_ACTION_ID" in credenciais_google_existentes else "",
            key=f"google_conv_{usuario['id']}"
        )

        if st.button("💾 Salvar credenciais Google", key=f"google_save_{usuario['id']}"):
            credenciais_google = [
                ("CLIENT_ID", google_client_id),
                ("REFRESH_TOKEN", google_refresh_token),
                ("DEVELOPER_TOKEN", google_dev_token),
                ("CUSTOMER_ID", google_cust_id),
                ("CONVERSION_ACTION_ID", google_conv_action_id),
            ]

            campos_vazios = [chave for chave, valor in credenciais_google if not valor.strip()]
            if campos_vazios:
                st.error(f"❌ Preencha todos os campos: {', '.join(campos_vazios)}")
            else:
                try:
                    for chave, valor in credenciais_google:
                        if valor != "************":
                            cursor.execute("""
                                INSERT INTO credenciais (user_id, plataforma, chave, valor)
                                VALUES (%s, 'google', %s, %s)
                                ON CONFLICT(user_id, plataforma, chave) DO UPDATE SET valor = excluded.valor
                            """, (usuario["id"], chave, valor.strip()))
                    conn.commit()
                    st.success("✅ Credenciais do Google salvas com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar credenciais do Google: {str(e)}")


# ------------------- CONTROLE INDIVIDUAL DE ENVIO DE EVENTOS -------------------
st.divider()
st.subheader("🔧 Controle de Envio por Cliente")

for _, usuario in df_usuarios.iterrows():
    with st.expander(f"⚙️ Envio | {usuario['email']}"):
        cursor.execute("SELECT envio_ativado FROM users WHERE id = %s", (usuario["id"],))
        estado_atual = cursor.fetchone()[0]

        novo_estado = st.toggle(
            "Envio de eventos está ativado",
            value=estado_atual,
            key=f"envio_toggle_{usuario['id']}"
        )

        if novo_estado != estado_atual:
            cursor.execute(
                "UPDATE users SET envio_ativado = %s WHERE id = %s",
                (novo_estado, usuario["id"])
            )
            conn.commit()
            st.success(f"✅ Envio de eventos {'ativado' if novo_estado else 'desativado'} para {usuario['email']}")

# ------------------- VISUALIZAÇÃO DAS CREDENCIAIS POR USUÁRIO -------------------
st.divider()
st.subheader("🔎 Credenciais Vinculadas por Cliente")

query = """
    SELECT u.email AS cliente, c.plataforma, c.chave, '************' AS valor
    FROM credenciais c
    JOIN users u ON u.id = c.user_id
    ORDER BY u.email, c.plataforma, c.chave;
"""

df_credenciais = pd.read_sql_query(query, conn)
st.dataframe(df_credenciais, use_container_width=True)
