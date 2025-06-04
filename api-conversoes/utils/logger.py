import os
import json
from datetime import datetime

# Garante que a pasta de logs exista
os.makedirs("logs", exist_ok=True)

def gerar_nome_arquivo(base: str) -> str:
    """
    Gera nome de arquivo com base na data e nome base.
    Ex: 2025-05-31_eventos.log
    """
    data = datetime.utcnow().strftime("%Y-%m-%d")
    return f"{data}_{base}"

def registrar_log(nome_arquivo: str, dados: dict):
    """
    Salva uma entrada de log no arquivo desejado na pasta logs/.
    Cada linha é um JSON separado para facilitar parsing.
    """
    timestamp = datetime.utcnow().isoformat()
    dados_completos = {"timestamp": timestamp, **dados}

    caminho = os.path.join("logs", nome_arquivo)
    try:
        with open(caminho, "a", encoding="utf-8") as f:
            f.write(json.dumps(dados_completos, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOGGER] Falha ao salvar log: {e}")

# Funções específicas para logs

def log_evento_recebido(evento):
    registrar_log(gerar_nome_arquivo("eventos.log"), {
        "origem": evento.origem,
        "evento": evento.evento,
        "ip": evento.ip or "não informado",
        "user_agent": evento.user_agent or "não informado",
        "url": evento.url or "não informado",
    })

def log_sucesso_google(resposta, evento):
    registrar_log(gerar_nome_arquivo("sucesso_google.log"), {
        "evento": evento.evento,
        "gclid": evento.gclid or "não informado",
        "resposta": str(resposta),
    })

def log_erro_google(erro, evento):
    registrar_log(gerar_nome_arquivo("erro_google.log"), {
        "evento": evento.evento,
        "gclid": evento.gclid or "não informado",
        "erro": str(erro),
    })

def log_sucesso_meta(resposta, evento):
    registrar_log(gerar_nome_arquivo("sucesso_meta.log"), {
        "evento": evento.evento,
        "fbclid": evento.fbclid or "não informado",
        "resposta": str(resposta),
    })

def log_erro_meta(erro, evento):
    registrar_log(gerar_nome_arquivo("erro_meta.log"), {
        "evento": evento.evento,
        "fbclid": evento.fbclid or "não informado",
        "erro": str(erro),
    })

def log_erro_geral(mensagem, contexto=None):
    registrar_log(gerar_nome_arquivo("erros_gerais.log"), {
        "mensagem": mensagem,
        "contexto": contexto or {},
    })
