import sqlite3

CAMINHO_DB = "users.db"

def get_envio_ativado() -> bool:
    """Retorna True se o envio de eventos estiver ativado, senão False."""
    conn = sqlite3.connect(CAMINHO_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT envio_ativado FROM configuracoes WHERE id = 1")
    resultado = cursor.fetchone()
    conn.close()
    return bool(resultado[0]) if resultado else False

def set_envio_ativado(valor: bool):
    """Atualiza a flag de envio_ativado (True para ativado, False para desativado)."""
    conn = sqlite3.connect(CAMINHO_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE configuracoes SET envio_ativado = ? WHERE id = 1", (int(valor),))
    conn.commit()
    conn.close()
