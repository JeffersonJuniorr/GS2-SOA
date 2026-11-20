"""
Enumerações do Domínio Central da CitizenTech Deslocai.
"""

from enum import Enum


class TransportMode(str, Enum):
    METRO = "METRO"
    TREM = "TREM"
    ONIBUS = "ONIBUS"
    INTEGRACAO_MULTIMODAL = "INTEGRACAO_MULTIMODAL"


class CrowdingLevel(str, Enum):
    BAIXA = "BAIXA"
    MODERADA = "MODERADA"
    ALTA = "ALTA"
    SUPERLOTADO = "SUPERLOTADO"


class RiskLevel(str, Enum):
    NORMAL = "NORMAL"
    ATENCAO = "ATENCAO"
    CRITICO = "CRITICO"


class EquipmentType(str, Enum):
    ELEVADOR_PCD = "ELEVADOR_PCD"
    ESCADA_ROLANTE = "ESCADA_ROLANTE"
    PLATAFORMA_ELEVATORIA = "PLATAFORMA_ELEVATORIA"
    PISO_TATIL_SONORO = "PISO_TATIL_SONORO"


class EquipmentStatus(str, Enum):
    OPERANTE = "OPERANTE"
    INOPERANTE = "INOPERANTE"
    MANUTENCAO = "MANUTENCAO"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
