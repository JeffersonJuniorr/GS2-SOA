"""
Controladores REST API (Camada de Apresentação SOA) da CitizenTech Deslocai.
Documentados automaticamente via OpenAPI 3.1 / Swagger UI (/docs).
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.migrations import run_migrations
from app.infrastructure.models import SchemaMigrationModel
from app.application.schemas import (
    StationCreateDTO,
    StationResponseDTO,
    EquipmentResponseDTO,
    EquipmentStatusUpdateDTO,
    TelemetryIngestDTO,
    TelemetryResponseDTO,
    CitizenAlertCreateDTO,
    CitizenAlertResponseDTO,
    MLPredictionRequestDTO,
    MLPredictionResponseDTO,
)
from app.application.services import DeslocaiApplicationService, MLPredictionService

router = APIRouter(prefix="/api/v1")


# ============================================================================
# 1. HEALTHCHECK & MIGRAÇÕES DE BANCO DE DADOS
# ============================================================================
@router.get(
    "/health",
    tags=["1. Governança SOA & Banco de Dados"],
    summary="Verifica integridade do serviço, banco de dados e modelo ML",
)
def health_check(db: Session = Depends(get_db)):
    migrations_count = db.query(SchemaMigrationModel).count()
    return {
        "status": "UP",
        "citizen_tech": "Deslocai",
        "version": "1.0.0",
        "database_connected": True,
        "applied_migrations_count": migrations_count,
        "ods_connected": ["ODS 9", "ODS 10", "ODS 11"],
    }


@router.get(
    "/system/migrations",
    tags=["1. Governança SOA & Banco de Dados"],
    summary="Lista o histórico de migrações versionadas aplicadas no banco de dados",
)
def list_migrations(db: Session = Depends(get_db)):
    applied = run_migrations(db)
    records = db.query(SchemaMigrationModel).order_by(SchemaMigrationModel.version.asc()).all()
    return {
        "total_migrations": len(records),
        "migrations": [
            {
                "version": r.version,
                "description": r.description,
                "applied_at": r.applied_at.isoformat() if r.applied_at else None,
            }
            for r in records
        ],
        "sync_status": applied,
    }


# ============================================================================
# 2. ESTAÇÕES E TERMINAIS DE TRANSPORTE PÚBLICO
# ============================================================================
@router.get(
    "/stations",
    response_model=List[StationResponseDTO],
    tags=["2. Estações & Mobilidade Urbana"],
    summary="Lista todas as estações monitoradas com lotação, clima e score de acessibilidade",
)
def list_stations(
    risk_level: Optional[str] = Query(
        default=None, description="Filtrar por nível de risco (NORMAL, ATENCAO, CRITICO)"
    ),
    transport_mode: Optional[str] = Query(
        default=None, description="Filtrar por modal (METRO, TREM, ONIBUS, INTEGRACAO_MULTIMODAL)"
    ),
    db: Session = Depends(get_db),
):
    service = DeslocaiApplicationService(db)
    return service.list_stations(risk_level=risk_level, transport_mode=transport_mode)


@router.get(
    "/stations/{station_code}",
    response_model=StationResponseDTO,
    tags=["2. Estações & Mobilidade Urbana"],
    summary="Consulta detalhes em tempo real de uma estação pelo código (ex: EST-SE-01)",
)
def get_station(station_code: str, db: Session = Depends(get_db)):
    service = DeslocaiApplicationService(db)
    return service.get_station_by_code(station_code)


@router.post(
    "/stations",
    response_model=StationResponseDTO,
    status_code=status.HTTP_201_CREATED,
    tags=["2. Estações & Mobilidade Urbana"],
    summary="Cadastra uma nova estação ou terminal no monitoramento Deslocai",
)
def create_station(payload: StationCreateDTO, db: Session = Depends(get_db)):
    service = DeslocaiApplicationService(db)
    return service.create_station(payload)


# ============================================================================
# 3. ACESSIBILIDADE (ELEVADORES PCD, ESCADAS ROLANTES E ROTAS SEGURAS)
# ============================================================================
@router.get(
    "/stations/{station_code}/equipments",
    response_model=List[EquipmentResponseDTO],
    tags=["3. Acessibilidade PCD & Idosos"],
    summary="Lista todos os elevadores PCD e escadas rolantes de uma estação",
)
def list_station_equipments(station_code: str, db: Session = Depends(get_db)):
    service = DeslocaiApplicationService(db)
    station = service.get_station_by_code(station_code)
    return station.equipments


@router.patch(
    "/equipments/{equipment_code}/status",
    response_model=EquipmentResponseDTO,
    tags=["3. Acessibilidade PCD & Idosos"],
    summary="Atualiza o estado operacional de um elevador ou escada rolante e recalcula o Score PCD",
)
def update_equipment_status(
    equipment_code: str,
    payload: EquipmentStatusUpdateDTO,
    db: Session = Depends(get_db),
):
    service = DeslocaiApplicationService(db)
    return service.update_equipment_status(equipment_code, payload)


@router.get(
    "/routes/accessible-recommendations",
    tags=["3. Acessibilidade PCD & Idosos"],
    summary="Recomenda estações acessíveis e seguras para PCDs/Idosos e calcula indicadores de impacto ODS",
)
def get_accessible_route_recommendations(db: Session = Depends(get_db)):
    service = DeslocaiApplicationService(db)
    return service.recommend_accessible_routes()


# ============================================================================
# 4. INGESTÃO DE TELEMETRIA IOT (ESP32 WOKWI)
# ============================================================================
@router.post(
    "/telemetry",
    response_model=TelemetryResponseDTO,
    status_code=status.HTTP_201_CREATED,
    tags=["4. Physical Computing IoT (ESP32 Wokwi)"],
    summary="Recebe telemetria em tempo real do Totem IoT ESP32 (Temperatura, Lotação, Elevador, SOS PCD)",
)
def ingest_telemetry(payload: TelemetryIngestDTO, db: Session = Depends(get_db)):
    service = DeslocaiApplicationService(db)
    return service.ingest_iot_telemetry(payload)


@router.get(
    "/telemetry",
    response_model=List[TelemetryResponseDTO],
    tags=["4. Physical Computing IoT (ESP32 Wokwi)"],
    summary="Lista o histórico recente de pacotes de telemetria enviados pelos nós ESP32",
)
def list_telemetry(
    station_id: Optional[int] = Query(default=None, description="Filtrar por ID da estação"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = DeslocaiApplicationService(db)
    return service.telemetry_repo.list_recent(station_id=station_id, limit=limit)


# ============================================================================
# 5. ALERTAS AO CIDADÃO E ZELADORIA COLABORATIVA
# ============================================================================
@router.get(
    "/alerts",
    response_model=List[CitizenAlertResponseDTO],
    tags=["5. Alertas em Tempo Real ao Cidadão"],
    summary="Lista os alertas ativos de superlotação, calor extremo e falha de elevadores",
)
def list_active_alerts(
    station_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    service = DeslocaiApplicationService(db)
    return service.alert_repo.list_active(station_id=station_id)


@router.post(
    "/alerts",
    response_model=CitizenAlertResponseDTO,
    status_code=status.HTTP_201_CREATED,
    tags=["5. Alertas em Tempo Real ao Cidadão"],
    summary="Registra um novo alerta colaborativo reportado por passageiro ou agente de estação",
)
def create_alert(payload: CitizenAlertCreateDTO, db: Session = Depends(get_db)):
    service = DeslocaiApplicationService(db)
    return service.create_citizen_alert(payload)


@router.patch(
    "/alerts/{alert_id}/resolve",
    response_model=CitizenAlertResponseDTO,
    tags=["5. Alertas em Tempo Real ao Cidadão"],
    summary="Marca um alerta como resolvido após normalização do equipamento ou fluxo",
)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    service = DeslocaiApplicationService(db)
    return service.resolve_alert(alert_id)


# ============================================================================
# 6. INTELIGÊNCIA ARTIFICIAL & MACHINE LEARNING (PREDIÇÃO EM TEMPO REAL)
# ============================================================================
@router.post(
    "/ml/predict-risk",
    response_model=MLPredictionResponseDTO,
    tags=["6. Inteligência Artificial & Machine Learning"],
    summary="Executa predição de Atraso Crítico no modelo Random Forest treinado com dados SP156 + INMET",
)
def predict_ml_risk(payload: MLPredictionRequestDTO):
    return MLPredictionService.predict_delay_risk(payload)


@router.get(
    "/ml/metrics",
    tags=["6. Inteligência Artificial & Machine Learning"],
    summary="Retorna as métricas auditáveis de Treino, Teste e GridSearchCV (18 combinações) do modelo ML",
)
def get_ml_metrics():
    return MLPredictionService.get_model_metrics()
