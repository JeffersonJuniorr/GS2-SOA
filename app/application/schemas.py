"""
Schemas DTO (Pydantic v2) com validações estritas e exemplos OpenAPI/Swagger
para todos os endpoints REST da CitizenTech Deslocai.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.domain.enums import (
    TransportMode,
    CrowdingLevel,
    RiskLevel,
    EquipmentType,
    EquipmentStatus,
    AlertSeverity,
)


class EquipmentResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    station_id: int
    code: str
    name: str
    equipment_type: EquipmentType
    location_description: str
    status: EquipmentStatus
    last_maintenance_note: str
    updated_at: Optional[datetime] = None


class EquipmentStatusUpdateDTO(BaseModel):
    status: EquipmentStatus = Field(
        ...,
        description="Novo estado operacional do equipamento (OPERANTE, INOPERANTE, MANUTENCAO).",
        examples=["INOPERANTE"],
    )
    last_maintenance_note: str = Field(
        default="Atualização via painel de manutenção / sensor IoT.",
        min_length=3,
        max_length=255,
        description="Observação técnica sobre a ocorrência ou reparo.",
        examples=["Falha elétrica na botoeira do elevador PCD."],
    )


class StationCreateDTO(BaseModel):
    code: str = Field(..., min_length=3, max_length=32, examples=["EST-VMA-06"])
    name: str = Field(..., min_length=3, max_length=120, examples=["Estação Vila Mariana"])
    line_name: str = Field(..., min_length=3, max_length=80, examples=["Linha 1-Azul"])
    transport_mode: TransportMode = Field(default=TransportMode.METRO)
    district: str = Field(..., min_length=2, max_length=80, examples=["VILA MARIANA"])
    latitude: float = Field(..., ge=-90.0, le=90.0, examples=[-23.5895])
    longitude: float = Field(..., ge=-180.0, le=180.0, examples=[-46.6346])
    daily_passengers_avg: int = Field(default=65000, ge=0, examples=[65000])


class StationResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    line_name: str
    transport_mode: str
    district: str
    latitude: float
    longitude: float
    daily_passengers_avg: int
    current_occupancy_pct: int
    current_temperature_c: float
    current_humidity_pct: float
    current_heat_index_c: float
    crowding_level: str
    risk_level: str
    accessibility_score: int
    pcd_sos_active: bool
    estimated_wait_minutes: float = 3.5
    equipments: List[EquipmentResponseDTO] = []


class TelemetryIngestDTO(BaseModel):
    """
    Payload enviado pelo Totem IoT ESP32 (Wokwi) para o Backend SOA.
    Compatível campo a campo com `sketch.ino`.
    """

    node_id: str = Field(..., min_length=3, max_length=64, examples=["DESLOCAI-IOT-ESP32-01"])
    station_code: str = Field(..., min_length=3, max_length=32, examples=["EST-SE-01"])
    station_name: Optional[str] = Field(default=None, examples=["Estacao Se - Linha 3 Vermelha"])
    temperature_c: float = Field(..., ge=-10.0, le=65.0, examples=[33.4])
    humidity_pct: float = Field(..., ge=0.0, le=100.0, examples=[68.0])
    heat_index_c: Optional[float] = Field(default=None, examples=[41.2])
    distance_cm: int = Field(default=100, ge=0, le=500, examples=[35])
    occupancy_pct: int = Field(..., ge=0, le=100, examples=[92])
    crowding_level: Optional[CrowdingLevel] = Field(default=None, examples=["SUPERLOTADO"])
    elevator_operational: bool = Field(..., examples=[False])
    escalator_operational: bool = Field(..., examples=[True])
    pcd_sos_active: bool = Field(default=False, examples=[True])
    risk_level: Optional[RiskLevel] = Field(default=None, examples=["CRITICO"])


class TelemetryResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    station_id: int
    node_id: str
    temperature_c: float
    humidity_pct: float
    heat_index_c: float
    distance_cm: int
    occupancy_pct: int
    crowding_level: str
    elevator_operational: bool
    escalator_operational: bool
    pcd_sos_active: bool
    risk_level: str
    recorded_at: Optional[datetime] = None


class CitizenAlertCreateDTO(BaseModel):
    station_code: str = Field(..., min_length=3, max_length=32, examples=["EST-SE-01"])
    title: str = Field(..., min_length=5, max_length=150, examples=["Elevador PCD parado no acesso Norte"])
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        examples=["Passageiro cadeirante aguarda apoio próximo à catraca central."],
    )
    category: str = Field(default="ACESSIBILIDADE_PCD", examples=["ACESSIBILIDADE_PCD"])
    severity: AlertSeverity = Field(default=AlertSeverity.CRITICAL)
    reported_by: str = Field(default="CIDADAO_APP", examples=["CIDADAO_PCD_VERIFICADO"])


class CitizenAlertResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    station_id: int
    title: str
    description: str
    category: str
    severity: str
    reported_by: str
    is_active: bool
    created_at: Optional[datetime] = None


class MLPredictionRequestDTO(BaseModel):
    """
    Parâmetros de entrada para predição em tempo real no modelo Random Forest
    treinado com dados reais do SP156 + INMET (2024).
    """

    temp_max_c: float = Field(default=32.8, ge=0.0, le=50.0, examples=[33.5])
    temp_min_c: float = Field(default=21.0, ge=-5.0, le=45.0, examples=[22.0])
    umidade_media_pct: float = Field(default=65.0, ge=10.0, le=100.0, examples=[68.0])
    precipitacao_total_mm: float = Field(default=8.5, ge=0.0, le=300.0, examples=[12.4])
    categoria_deslocai: str = Field(
        default="INFRA_ESTACAO_E_PONTO",
        examples=["INFRA_ESTACAO_E_PONTO"],
        description="Opções: INFRA_ESTACAO_E_PONTO, SUPERLOTACAO_E_INTERVALO, ACESSIBILIDADE_PCD, OPERACAO_EMBARQUE, CIRCULACAO_E_VIAS, ATENDIMENTO_IDOSO, BILHETE_UNICO_E_TARIFA",
    )
    meio_comunicacao: str = Field(default="MOBILE", examples=["MOBILE"])
    tema: str = Field(default="Trânsito e Transporte", examples=["Trânsito e Transporte"])
    orgao_agrupado: str = Field(default="INTEGRACAO-SPTRANS", examples=["INTEGRACAO-SPTRANS"])
    regiao_sp: str = Field(default="SE", examples=["SE"])
    volume_chamados_dia: int = Field(default=62, ge=1, le=500, examples=[75])


class MLPredictionResponseDTO(BaseModel):
    predicted_critical_delay: bool
    probability_critical_delay: float
    risk_classification: str
    citizen_recommendation: str
    model_used: str
    dataset_source: str
