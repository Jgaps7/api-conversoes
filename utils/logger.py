import os
import json
from datetime import datetime

# Garante que a pasta de logs exista
os.makedirs("logs", exist_ok=True)

def gerar_nome_arquivo(base: str) -> str:
    data = datetime.utcnow().strftime("%Y-%m-%d")
    return f"{data}_{base}"

def registrar_log(nome_arquivo: str, dados: dict):
    timestamp = datetime.utcnow().isoformat()
    dados_completos = {"timestamp": timestamp, **dados}

    caminho = os.path.join("logs", nome_arquivo)
    try:
        with open(caminho, "a", encoding="utf-8") as f:
            f.write(json.dumps(dados_completos, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOGGER] Falha ao salvar log: {e}")

# Função robusta para pegar campos tanto de objeto quanto de dict
def get_attr(evento, campo, default="não informado"):
    if isinstance(evento, dict):
        return evento.get(campo, default)
    return getattr(evento, campo, default)

# Funções específicas para logs

def log_evento_recebido(evento):
    registrar_log(gerar_nome_arquivo("eventos.log"), {
        "origem": get_attr(evento, "origem"),
        "evento": get_attr(evento, "evento"),
        "ip": get_attr(evento, "ip"),
        "user_agent": get_attr(evento, "user_agent"),
        "url": get_attr(evento, "url"),
    })

def log_sucesso_google(resposta, evento):
    registrar_log(gerar_nome_arquivo("sucesso_google.log"), {
        "evento": get_attr(evento, "evento"),
        "gclid": get_attr(evento, "gclid"),
        "resposta": str(resposta),
    })

def log_erro_google(erro, evento):
    registrar_log(gerar_nome_arquivo("erro_google.log"), {
        "evento": get_attr(evento, "evento"),
        "gclid": get_attr(evento, "gclid"),
        "erro": str(erro),
    })

def log_sucesso_meta(resposta, evento):
    registrar_log(gerar_nome_arquivo("sucesso_meta.log"), {
        "evento": get_attr(evento, "evento"),
        "fbclid": get_attr(evento, "fbclid"),
        "resposta": str(resposta),
    })

def log_erro_meta(erro, evento):
    registrar_log(gerar_nome_arquivo("erro_meta.log"), {
        "evento": get_attr(evento, "evento"),
        "fbclid": get_attr(evento, "fbclid"),
        "erro": str(erro),
    })

def log_erro_geral(mensagem, contexto=None):
    registrar_log(gerar_nome_arquivo("erros_gerais.log"), {
        "mensagem": mensagem,
        "contexto": contexto or {},
    })
