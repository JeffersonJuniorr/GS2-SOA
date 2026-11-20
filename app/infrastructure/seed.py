"""
Seed inicial idempotente de dados reais de estações e terminais de São Paulo
para demonstração imediata da API SOA Deslocai.
"""

from sqlalchemy.orm import Session
from app.infrastructure.models import (
    StationModel,
    AccessibilityEquipmentModel,
    TelemetryReadingModel,
    CitizenAlertModel,
)


def seed_initial_data(db: Session) -> None:
    if db.query(StationModel).count() > 0:
        return

    stations_data = [
        StationModel(
            code="EST-SE-01",
            name="Estação Sé",
            line_name="Linha 1-Azul / Linha 3-Vermelha",
            transport_mode="METRO",
            district="SE",
            latitude=-23.5505,
            longitude=-46.6333,
            daily_passengers_avg=368000,
            current_occupancy_pct=92,
            current_temperature_c=33.2,
            current_humidity_pct=67.0,
            current_heat_index_c=40.8,
            crowding_level="SUPERLOTADO",
            risk_level="CRITICO",
            accessibility_score=30,
            pcd_sos_active=False,
        ),
        StationModel(
            code="EST-LUZ-02",
            name="Estação da Luz",
            line_name="Linha 1-Azul / Linha 4-Amarela / CPTM",
            transport_mode="INTEGRACAO_MULTIMODAL",
            district="BOM RETIRO",
            latitude=-23.5345,
            longitude=-46.6352,
            daily_passengers_avg=266000,
            current_occupancy_pct=74,
            current_temperature_c=29.1,
            current_humidity_pct=62.0,
            current_heat_index_c=32.4,
            crowding_level="ALTA",
            risk_level="ATENCAO",
            accessibility_score=72,
            pcd_sos_active=False,
        ),
        StationModel(
            code="EST-BFU-03",
            name="Palmeiras - Barra Funda",
            line_name="Linha 3-Vermelha / CPTM / Terminal SPTrans",
            transport_mode="INTEGRACAO_MULTIMODAL",
            district="BARRA FUNDA",
            latitude=-23.5255,
            longitude=-46.6673,
            daily_passengers_avg=195000,
            current_occupancy_pct=48,
            current_temperature_c=26.2,
            current_humidity_pct=58.0,
            current_heat_index_c=26.9,
            crowding_level="MODERADA",
            risk_level="NORMAL",
            accessibility_score=100,
            pcd_sos_active=False,
        ),
        StationModel(
            code="EST-TAT-04",
            name="Estação Tatuapé",
            line_name="Linha 3-Vermelha / Linhas 11 e 12 CPTM",
            transport_mode="TREM",
            district="TATUAPE",
            latitude=-23.5403,
            longitude=-46.5766,
            daily_passengers_avg=182000,
            current_occupancy_pct=88,
            current_temperature_c=32.5,
            current_humidity_pct=65.0,
            current_heat_index_c=38.9,
            crowding_level="SUPERLOTADO",
            risk_level="CRITICO",
            accessibility_score=85,
            pcd_sos_active=False,
        ),
        StationModel(
            code="EST-PIN-05",
            name="Terminal e Estação Pinheiros",
            line_name="Linha 4-Amarela / Linha 9-Esmeralda / SPTrans",
            transport_mode="ONIBUS",
            district="PINHEIROS",
            latitude=-23.5673,
            longitude=-46.7019,
            daily_passengers_avg=158000,
            current_occupancy_pct=34,
            current_temperature_c=24.8,
            current_humidity_pct=55.0,
            current_heat_index_c=24.8,
            crowding_level="BAIXA",
            risk_level="NORMAL",
            accessibility_score=100,
            pcd_sos_active=False,
        ),
    ]

    db.add_all(stations_data)
    db.flush()

    equipments_data = [
        AccessibilityEquipmentModel(
            station_id=stations_data[0].id,
            code="EQ-SE-ELEV-01",
            name="Elevador PCD Acesso Praça da Sé -> Mezanino",
            equipment_type="ELEVADOR_PCD",
            location_description="Acesso Norte - Praça da Sé (Ao lado da bilheteria central)",
            status="INOPERANTE",
            last_maintenance_note="Falha no sensor de porta detectada pelo nó IoT ESP32.",
        ),
        AccessibilityEquipmentModel(
            station_id=stations_data[0].id,
            code="EQ-SE-ESC-01",
            name="Escada Rolante Transferência Linha 3 -> Linha 1",
            equipment_type="ESCADA_ROLANTE",
            location_description="Plataforma sentido Itaquera",
            status="OPERANTE",
            last_maintenance_note="Operando normalmente.",
        ),
        AccessibilityEquipmentModel(
            station_id=stations_data[1].id,
            code="EQ-LUZ-ELEV-01",
            name="Elevador PCD Integração Linha 4-Amarela",
            equipment_type="ELEVADOR_PCD",
            location_description="Túnel de transferência CPTM / Linha 4",
            status="OPERANTE",
            last_maintenance_note="Revisão concluída.",
        ),
        AccessibilityEquipmentModel(
            station_id=stations_data[1].id,
            code="EQ-LUZ-ESC-01",
            name="Escada Rolante Acesso Parque da Luz",
            equipment_type="ESCADA_ROLANTE",
            location_description="Saída Rua Mauá",
            status="MANUTENCAO",
            last_maintenance_note="Manutenção preventiva programada.",
        ),
        AccessibilityEquipmentModel(
            station_id=stations_data[2].id,
            code="EQ-BFU-ELEV-01",
            name="Elevador PCD Plataforma Central Barra Funda",
            equipment_type="ELEVADOR_PCD",
            location_description="Acesso Terminal Rodoviário / Ônibus SPTrans",
            status="OPERANTE",
            last_maintenance_note="100% operacional.",
        ),
        AccessibilityEquipmentModel(
            station_id=stations_data[3].id,
            code="EQ-TAT-ELEV-01",
            name="Elevador PCD Passarela Shopping / CPTM",
            equipment_type="ELEVADOR_PCD",
            location_description="Mezanino Leste",
            status="OPERANTE",
            last_maintenance_note="Operando normalmente.",
        ),
        AccessibilityEquipmentModel(
            station_id=stations_data[4].id,
            code="EQ-PIN-ELEV-01",
            name="Elevador PCD Integração Terminal SPTrans Pinheiros",
            equipment_type="ELEVADOR_PCD",
            location_description="Passarela de integração Linha 9 / Terminal SPTrans",
            status="OPERANTE",
            last_maintenance_note="Operando normalmente.",
        ),
    ]
    db.add_all(equipments_data)

    telemetry_seed = [
        TelemetryReadingModel(
            station_id=stations_data[0].id,
            node_id="DESLOCAI-IOT-ESP32-01",
            temperature_c=33.2,
            humidity_pct=67.0,
            heat_index_c=40.8,
            distance_cm=38,
            occupancy_pct=92,
            crowding_level="SUPERLOTADO",
            elevator_operational=False,
            escalator_operational=True,
            pcd_sos_active=False,
            risk_level="CRITICO",
        ),
        TelemetryReadingModel(
            station_id=stations_data[2].id,
            node_id="DESLOCAI-IOT-ESP32-03",
            temperature_c=26.2,
            humidity_pct=58.0,
            heat_index_c=26.9,
            distance_cm=195,
            occupancy_pct=48,
            crowding_level="MODERADA",
            elevator_operational=True,
            escalator_operational=True,
            pcd_sos_active=False,
            risk_level="NORMAL",
        ),
    ]
    db.add_all(telemetry_seed)

    alerts_seed = [
        CitizenAlertModel(
            station_id=stations_data[0].id,
            title="Elevador PCD Inoperante e Calor Extremo na Estação Sé",
            description=(
                "O Totem IoT ESP32 detectou paralisação no Elevador EQ-SE-ELEV-01 (Acesso Praça da Sé) "
                "e sensação térmica de 40.8°C na plataforma. Recomendamos desembarque acessível na Estação República ou Barra Funda."
            ),
            category="ACESSIBILIDADE_E_CLIMA",
            severity="CRITICAL",
            reported_by="DESLOCAI-IOT-ESP32-01",
            is_active=True,
        ),
        CitizenAlertModel(
            station_id=stations_data[3].id,
            title="Superlotação Crítica na Plataforma Tatuapé (88%)",
            description="Tempo de espera estimado em 9.8 minutos. Elevadores PCD permanecem 100% operantes.",
            category="SUPERLOTACAO",
            severity="WARNING",
            reported_by="DESLOCAI-IOT-ESP32-04",
            is_active=True,
        ),
    ]
    db.add_all(alerts_seed)
    db.commit()
