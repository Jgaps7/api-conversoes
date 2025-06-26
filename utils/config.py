from supabase_conn import get_connection
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def get_envio_ativado(user_id: str) -> bool:
    """
    Retorna True se o envio estiver ativado para o user_id fornecido.
    Se não houver entrada, assume True por padrão.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT envio_ativado FROM controle_envio WHERE user_id = %s", (user_id,))
    resultado = cursor.fetchone()
    conn.close()
    return bool(resultado[0]) if resultado else True  # padrão ativado


def set_envio_ativado(user_id: str, valor: bool):
    """
    Define o estado de envio (True ou False) para um user_id específico.
    Cria ou atualiza a entrada na tabela controle_envio.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO controle_envio (user_id, envio_ativado)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET envio_ativado = EXCLUDED.envio_ativado
    """, (user_id, valor))
    conn.commit()
    conn.close()
