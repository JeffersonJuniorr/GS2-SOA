"""
Suíte Completa de Testes Automatizados (Unitários de Domínio + Integração de API REST)
para a disciplina de Arquitetura Orientada a Serviços (SOA) e Web Services.
"""

import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_deslocai.db"

from app.main import app
from app.infrastructure.database import Base, engine, SessionLocal
from app.infrastructure.migrations import run_migrations
from app.infrastructure.seed import seed_initial_data
from app.domain.enums import CrowdingLevel, RiskLevel, EquipmentType, EquipmentStatus
from app.domain.entities import DeslocaiDomainService, EquipmentDomainSnapshot


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_migrations(db)
        seed_initial_data(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# ============================================================================
# 1. TESTES UNITÁRIOS DA CAMADA DE DOMÍNIO (DDD)
# ============================================================================
def test_domain_heat_index_calculation():
    # Temperatura amena mantém valor original
    assert DeslocaiDomainService.compute_heat_index_c(24.0, 55.0) == 24.0
    # Calor extremo com alta umidade eleva significativamente a sensação térmica
    hi = DeslocaiDomainService.compute_heat_index_c(34.0, 70.0)
    assert hi > 38.0


def test_domain_crowding_classification():
    assert DeslocaiDomainService.classify_crowding(20) == CrowdingLevel.BAIXA
    assert DeslocaiDomainService.classify_crowding(50) == CrowdingLevel.MODERADA
    assert DeslocaiDomainService.classify_crowding(72) == CrowdingLevel.ALTA
    assert DeslocaiDomainService.classify_crowding(90) == CrowdingLevel.SUPERLOTADO


def test_domain_risk_level_evaluation():
    # Tudo normal
    assert (
        DeslocaiDomainService.evaluate_risk_level(
            occupancy_pct=40,
            temperature_c=25.0,
            elevator_operational=True,
            escalator_operational=True,
            pcd_sos_active=False,
        )
        == RiskLevel.NORMAL
    )
    # Elevador PCD inoperante eleva imediatamente para CRITICO
    assert (
        DeslocaiDomainService.evaluate_risk_level(
            occupancy_pct=25,
            temperature_c=23.0,
            elevator_operational=False,
            escalator_operational=True,
            pcd_sos_active=False,
        )
        == RiskLevel.CRITICO
    )
    # Escada rolante parada com plataforma normal -> ATENCAO
    assert (
        DeslocaiDomainService.evaluate_risk_level(
            occupancy_pct=40,
            temperature_c=25.0,
            elevator_operational=True,
            escalator_operational=False,
            pcd_sos_active=False,
        )
        == RiskLevel.ATENCAO
    )


def test_domain_accessibility_score_calculation():
    eq_ok = [
        EquipmentDomainSnapshot("EQ-1", EquipmentType.ELEVADOR_PCD, EquipmentStatus.OPERANTE),
        EquipmentDomainSnapshot("EQ-2", EquipmentType.ESCADA_ROLANTE, EquipmentStatus.OPERANTE),
    ]
    assert DeslocaiDomainService.calculate_accessibility_score(eq_ok, occupancy_pct=30) == 100

    eq_broken_elev = [
        EquipmentDomainSnapshot("EQ-1", EquipmentType.ELEVADOR_PCD, EquipmentStatus.INOPERANTE),
        EquipmentDomainSnapshot("EQ-2", EquipmentType.ESCADA_ROLANTE, EquipmentStatus.OPERANTE),
    ]
    score = DeslocaiDomainService.calculate_accessibility_score(
        eq_broken_elev, occupancy_pct=90, pcd_sos_active=True
    )
    assert score == 10  # 100 - 55 (elev) - 15 (lotação>=85) - 20 (SOS) = 10


# ============================================================================
# 2. TESTES DE INTEGRAÇÃO: GOVERNANÇA SOA, HEALTHCHECK E MIGRAÇÕES
# ============================================================================
def test_api_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["citizen_tech"] == "Deslocai"
    assert data["database_connected"] is True
    assert data["applied_migrations_count"] >= 4


def test_api_migrations_history():
    response = client.get("/api/v1/system/migrations")
    assert response.status_code == 200
    data = response.json()
    assert data["total_migrations"] == 4
    versions = [m["version"] for m in data["migrations"]]
    assert "V001__create_stations_table" in versions
    assert "V004__create_citizen_alerts_table" in versions


def test_dashboard_html_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Desloc" in response.text
    assert "/docs" in response.text


# ============================================================================
# 3. TESTES DE INTEGRAÇÃO: ESTAÇÕES E FILTROS (POSITIVOS E NEGATIVOS)
# ============================================================================
def test_list_all_stations():
    response = client.get("/api/v1/stations")
    assert response.status_code == 200
    stations = response.json()
    assert len(stations) >= 5
    codes = [s["code"] for s in stations]
    assert "EST-SE-01" in codes
    assert "EST-LUZ-02" in codes


def test_filter_stations_by_risk_level():
    response = client.get("/api/v1/stations?risk_level=CRITICO")
    assert response.status_code == 200
    stations = response.json()
    assert len(stations) >= 1
    assert all(s["risk_level"] == "CRITICO" for s in stations)


def test_get_station_by_code_success_and_not_found():
    res_ok = client.get("/api/v1/stations/EST-SE-01")
    assert res_ok.status_code == 200
    assert res_ok.json()["name"] == "Estação Sé"

    res_404 = client.get("/api/v1/stations/EST-INEXISTENTE-99")
    assert res_404.status_code == 404


def test_create_station_and_duplicate_conflict():
    payload = {
        "code": "EST-VMA-06",
        "name": "Estação Vila Mariana",
        "line_name": "Linha 1-Azul",
        "transport_mode": "METRO",
        "district": "VILA MARIANA",
        "latitude": -23.5895,
        "longitude": -46.6346,
        "daily_passengers_avg": 68000,
    }
    res_create = client.post("/api/v1/stations", json=payload)
    assert res_create.status_code == 201
    assert res_create.json()["code"] == "EST-VMA-06"

    # Tentativa duplicada deve retornar 409 Conflict
    res_dup = client.post("/api/v1/stations", json=payload)
    assert res_dup.status_code == 409


# ============================================================================
# 4. TESTES DE INTEGRAÇÃO: EQUIPAMENTOS PCD E ROTAS ACESSÍVEIS
# ============================================================================
def test_update_equipment_status_recalculates_accessibility_score():
    # Coloca elevador de Barra Funda em manutenção/inoperante
    res = client.patch(
        "/api/v1/equipments/EQ-BFU-ELEV-01/status",
        json={
            "status": "INOPERANTE",
            "last_maintenance_note": "Teste automatizado de falha no elevador PCD.",
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "INOPERANTE"

    # Verifica se o score de acessibilidade da estação caiu e o risco subiu para CRITICO
    st_res = client.get("/api/v1/stations/EST-BFU-03")
    st_data = st_res.json()
    assert st_data["accessibility_score"] <= 45
    assert st_data["risk_level"] == "CRITICO"

    # Restaura o elevador para OPERANTE
    client.patch(
        "/api/v1/equipments/EQ-BFU-ELEV-01/status",
        json={"status": "OPERANTE", "last_maintenance_note": "Elevador restabelecido."},
    )


def test_accessible_route_recommendations():
    res = client.get("/api/v1/routes/accessible-recommendations")
    assert res.status_code == 200
    data = res.json()
    assert "safe_accessible_stations" in data
    assert "critical_stations_to_avoid_for_pcd" in data
    assert "ODS 10" in data["impact_indicator"]["ods_alignment"]


# ============================================================================
# 5. TESTES DE INTEGRAÇÃO: TELEMETRIA IOT ESP32 (WOKWI)
# ============================================================================
def test_ingest_iot_telemetry_from_esp32():
    esp32_payload = {
        "node_id": "DESLOCAI-IOT-ESP32-01",
        "station_code": "EST-PIN-05",
        "station_name": "Terminal e Estacao Pinheiros",
        "temperature_c": 34.2,
        "humidity_pct": 70.0,
        "distance_cm": 28,
        "occupancy_pct": 95,
        "elevator_operational": False,
        "escalator_operational": True,
        "pcd_sos_active": True,
    }
    res = client.post("/api/v1/telemetry", json=esp32_payload)
    assert res.status_code == 201
    t_data = res.json()
    assert t_data["risk_level"] == "CRITICO"
    assert t_data["crowding_level"] == "SUPERLOTADO"
    assert t_data["heat_index_c"] > 38.0


def test_ingest_iot_telemetry_validation_error_negative():
    # Ocupação acima de 100% deve ser rejeitada com HTTP 422 Unprocessable Entity
    invalid_payload = {
        "node_id": "DESLOCAI-IOT-ESP32-01",
        "station_code": "EST-SE-01",
        "temperature_c": 26.0,
        "humidity_pct": 60.0,
        "occupancy_pct": 145,
        "elevator_operational": True,
        "escalator_operational": True,
    }
    res = client.post("/api/v1/telemetry", json=invalid_payload)
    assert res.status_code == 422


# ============================================================================
# 6. TESTES DE INTEGRAÇÃO: ALERTAS E PREDIÇÃO DE MACHINE LEARNING
# ============================================================================
def test_create_and_resolve_citizen_alert():
    create_res = client.post(
        "/api/v1/alerts",
        json={
            "station_code": "EST-LUZ-02",
            "title": "Fila extensa no elevador de transferência",
            "description": "Mais de 15 minutos de espera para cadeirantes no acesso da Linha 4.",
            "category": "ACESSIBILIDADE_PCD",
            "severity": "WARNING",
            "reported_by": "PASSAGEIRO_PCD_01",
        },
    )
    assert create_res.status_code == 201
    alert_id = create_res.json()["id"]

    resolve_res = client.patch(f"/api/v1/alerts/{alert_id}/resolve")
    assert resolve_res.status_code == 200
    assert resolve_res.json()["is_active"] is False


def test_ml_prediction_and_metrics_endpoints():
    metrics_res = client.get("/api/v1/ml/metrics")
    assert metrics_res.status_code == 200
    m_data = metrics_res.json()
    assert m_data["dataset_total_rows"] == 17990
    assert m_data["best_rf_metrics"]["test_roc_auc"] > 0.95

    pred_res = client.post(
        "/api/v1/ml/predict-risk",
        json={
            "temp_max_c": 34.0,
            "temp_min_c": 22.0,
            "umidade_media_pct": 68.0,
            "precipitacao_total_mm": 18.0,
            "categoria_deslocai": "INFRA_ESTACAO_E_PONTO",
            "meio_comunicacao": "MOBILE",
            "tema": "Trânsito e Transporte",
            "orgao_agrupado": "INTEGRACAO-SPTRANS",
            "regiao_sp": "SE",
            "volume_chamados_dia": 85,
        },
    )
    assert pred_res.status_code == 200
    p_data = pred_res.json()
    assert "probability_critical_delay" in p_data
    assert 0.0 <= p_data["probability_critical_delay"] <= 1.0
