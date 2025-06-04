# models/event.py

from pydantic import BaseModel
from typing import Optional

class EventoConversao(BaseModel):
    # Identificação do usuário
    email: Optional[str] = None
    telefone: Optional[str] = None
    nome: Optional[str] = None
    user_id: Optional[str] = None

    # Informações técnicas do navegador
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    url: Optional[str] = None
    referrer: Optional[str] = None
    pagina_destino: Optional[str] = None
    botao_clicado: Optional[str] = None

    # IDs de rastreamento
    gclid: Optional[str] = None
    fbclid: Optional[str] = None
    fbp: Optional[str] = None
    fbc: Optional[str] = None
    click_id: Optional[str] = None

    # Informações de localização
    cidade: Optional[str] = None
    regiao: Optional[str] = None
    pais: Optional[str] = None

    # UTM (para futuras análises de campanhas)
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

    # Campos obrigatórios
    origem: str  # 'google' ou 'meta'
    evento: str  # exemplo: 'lead', 'purchase', etc.
