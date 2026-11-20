"""
Regras de Negócio e Serviços Puros de Domínio (Clean Architecture / DDD)
para a CitizenTech Deslocai.
"""

import math
from dataclasses import dataclass
from typing import List
from app.domain.enums import (
    CrowdingLevel,
    RiskLevel,
    EquipmentStatus,
    EquipmentType,
)


@dataclass(frozen=True)
class EquipmentDomainSnapshot:
    code: str
    equipment_type: EquipmentType
    status: EquipmentStatus


class DeslocaiDomainService:
    """
    Encapsula as regras de negócio centrais do Deslocai sem acoplamento
    com frameworks web ou banco de dados.
    """

    TEMP_WARNING_C: float = 28.0
    TEMP_CRITICAL_C: float = 32.0
    OCCUPANCY_WARNING_PCT: int = 65
    OCCUPANCY_CRITICAL_PCT: int = 85

    @staticmethod
    def compute_heat_index_c(temperature_c: float, humidity_pct: float) -> float:
        """
        Calcula a sensação térmica (Heat Index) em °C combinando temperatura
        de bulbo seco e umidade relativa do ar.
        """
        if temperature_c < 26.0 or humidity_pct < 40.0:
            return round(temperature_c, 1)
        vapor_pressure = (humidity_pct / 100.0) * 6.105 * math.exp(
            (17.27 * temperature_c) / (237.7 + temperature_c)
        )
        heat_index = temperature_c + 0.33 * vapor_pressure - 4.0
        return round(max(heat_index, temperature_c), 1)

    @classmethod
    def classify_crowding(cls, occupancy_pct: int) -> CrowdingLevel:
        """Classifica o nível de lotação da plataforma/vagão a partir da ocupação (0-100%)."""
        if occupancy_pct >= cls.OCCUPANCY_CRITICAL_PCT:
            return CrowdingLevel.SUPERLOTADO
        if occupancy_pct >= cls.OCCUPANCY_WARNING_PCT:
            return CrowdingLevel.ALTA
        if occupancy_pct >= 35:
            return CrowdingLevel.MODERADA
        return CrowdingLevel.BAIXA

    @classmethod
    def evaluate_risk_level(
        cls,
        occupancy_pct: int,
        temperature_c: float,
        elevator_operational: bool,
        escalator_operational: bool,
        pcd_sos_active: bool = False,
    ) -> RiskLevel:
        """
        Determina o nível de risco global para o cidadão na estação combinando
        lotação, estresse térmico e disponibilidade de equipamentos PCD.
        """
        if (
            not elevator_operational
            or pcd_sos_active
            or occupancy_pct >= cls.OCCUPANCY_CRITICAL_PCT
            or temperature_c >= cls.TEMP_CRITICAL_C
        ):
            return RiskLevel.CRITICO

        if (
            not escalator_operational
            or occupancy_pct >= cls.OCCUPANCY_WARNING_PCT
            or temperature_c >= cls.TEMP_WARNING_C
        ):
            return RiskLevel.ATENCAO

        return RiskLevel.NORMAL

    @staticmethod
    def calculate_accessibility_score(
        equipments: List[EquipmentDomainSnapshot],
        occupancy_pct: int,
        pcd_sos_active: bool = False,
    ) -> int:
        """
        Calcula o Score de Acessibilidade da estação (0 a 100 pontos) para
        orientar pessoas com deficiência (PCD), cadeirantes e idosos.
        - Elevador PCD inoperante reduz drasticamente o score (-55 pts cada).
        - Escada rolante inoperante reduz moderadamente (-20 pts cada).
        - Superlotação (>= 85%) dificulta mobilidade de cadeirantes (-15 pts).
        - SOS PCD ativo sinaliza incidente em andamento (-20 pts).
        """
        score = 100
        for eq in equipments:
            if eq.status != EquipmentStatus.OPERANTE:
                if eq.equipment_type in (
                    EquipmentType.ELEVADOR_PCD,
                    EquipmentType.PLATAFORMA_ELEVATORIA,
                ):
                    score -= 55
                elif eq.equipment_type == EquipmentType.ESCADA_ROLANTE:
                    score -= 20
                else:
                    score -= 10

        if occupancy_pct >= 85:
            score -= 15
        elif occupancy_pct >= 65:
            score -= 8

        if pcd_sos_active:
            score -= 20

        return max(0, min(100, score))

    @staticmethod
    def estimate_wait_time_minutes(occupancy_pct: int, base_headway_min: float = 3.5) -> float:
        """
        Estima o tempo real de espera na plataforma (em minutos).
        Quando a ocupação supera 80%, passageiros frequentemente não conseguem
        embarcar no primeiro trem/ônibus, multiplicando o tempo de espera.
        """
        if occupancy_pct >= 90:
            multiplier = 2.8
        elif occupancy_pct >= 75:
            multiplier = 1.9
        elif occupancy_pct >= 50:
            multiplier = 1.3
        else:
            multiplier = 1.0
        return round(base_headway_min * multiplier, 1)
