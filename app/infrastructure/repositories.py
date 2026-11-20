"""
Camada de Repositórios (Repository Pattern) para abstração de persistência no SQLAlchemy.
"""

from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.infrastructure.models import (
    StationModel,
    AccessibilityEquipmentModel,
    TelemetryReadingModel,
    CitizenAlertModel,
)


class StationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, risk_level: Optional[str] = None, transport_mode: Optional[str] = None) -> list[StationModel]:
        query = self.db.query(StationModel).options(joinedload(StationModel.equipments))
        if risk_level:
            query = query.filter(StationModel.risk_level == risk_level.upper())
        if transport_mode:
            query = query.filter(StationModel.transport_mode == transport_mode.upper())
        return query.order_by(StationModel.code.asc()).all()

    def get_by_id(self, station_id: int) -> Optional[StationModel]:
        return (
            self.db.query(StationModel)
            .options(joinedload(StationModel.equipments), joinedload(StationModel.alerts))
            .filter(StationModel.id == station_id)
            .first()
        )

    def get_by_code(self, code: str) -> Optional[StationModel]:
        return (
            self.db.query(StationModel)
            .options(joinedload(StationModel.equipments), joinedload(StationModel.alerts))
            .filter(StationModel.code == code.upper())
            .first()
        )

    def create(self, station: StationModel) -> StationModel:
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station

    def save(self, station: StationModel) -> StationModel:
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station


class EquipmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_station(self, station_id: int) -> list[AccessibilityEquipmentModel]:
        return (
            self.db.query(AccessibilityEquipmentModel)
            .filter(AccessibilityEquipmentModel.station_id == station_id)
            .order_by(AccessibilityEquipmentModel.code.asc())
            .all()
        )

    def get_by_code(self, code: str) -> Optional[AccessibilityEquipmentModel]:
        return (
            self.db.query(AccessibilityEquipmentModel)
            .filter(AccessibilityEquipmentModel.code == code.upper())
            .first()
        )

    def save(self, eq: AccessibilityEquipmentModel) -> AccessibilityEquipmentModel:
        self.db.add(eq)
        self.db.commit()
        self.db.refresh(eq)
        return eq


class TelemetryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, reading: TelemetryReadingModel) -> TelemetryReadingModel:
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def list_recent(self, station_id: Optional[int] = None, limit: int = 25) -> list[TelemetryReadingModel]:
        query = self.db.query(TelemetryReadingModel)
        if station_id is not None:
            query = query.filter(TelemetryReadingModel.station_id == station_id)
        return query.order_by(TelemetryReadingModel.recorded_at.desc(), TelemetryReadingModel.id.desc()).limit(limit).all()


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, alert: CitizenAlertModel) -> CitizenAlertModel:
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def list_active(self, station_id: Optional[int] = None) -> list[CitizenAlertModel]:
        query = self.db.query(CitizenAlertModel).filter(CitizenAlertModel.is_active.is_(True))
        if station_id is not None:
            query = query.filter(CitizenAlertModel.station_id == station_id)
        return query.order_by(CitizenAlertModel.created_at.desc(), CitizenAlertModel.id.desc()).all()

    def get_by_id(self, alert_id: int) -> Optional[CitizenAlertModel]:
        return self.db.query(CitizenAlertModel).filter(CitizenAlertModel.id == alert_id).first()

    def save(self, alert: CitizenAlertModel) -> CitizenAlertModel:
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
