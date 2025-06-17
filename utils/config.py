from supabase_conn import get_connection
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def get_envio_ativado() -> bool:
    """
    Retorna True se o envio de eventos estiver ativado, senão False.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT envio_ativado FROM configuracoes WHERE id = 1")
    resultado = cursor.fetchone()
    conn.close()
    return bool(resultado[0]) if resultado else False

def set_envio_ativado(valor: bool):
    """
    Atualiza a flag de envio_ativado (True para ativado, False para desativado).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE configuracoes SET envio_ativado = %s WHERE id = 1", (int(valor),))
    conn.commit()
    conn.close()
