"""
Modelos ORM Relacionais (SQLAlchemy 2.0) para persistência da CitizenTech Deslocai.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SchemaMigrationModel(Base):
    """Tabela de controle de migrações versionadas aplicadas ao banco de dados."""

    __tablename__ = "schema_migrations"

    version: Mapped[str] = mapped_column(String(64), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class StationModel(Base):
    """Representa uma Estação de Metrô, Trem ou Terminal de Ônibus monitorado pelo Deslocai."""

    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    line_name: Mapped[str] = mapped_column(String(80), nullable=False)
    transport_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    district: Mapped[str] = mapped_column(String(80), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    daily_passengers_avg: Mapped[int] = mapped_column(Integer, default=50000, nullable=False)

    # Estado em tempo real atualizado pelo Totem IoT (ESP32)
    current_occupancy_pct: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    current_temperature_c: Mapped[float] = mapped_column(Float, default=25.0, nullable=False)
    current_humidity_pct: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    current_heat_index_c: Mapped[float] = mapped_column(Float, default=25.0, nullable=False)
    crowding_level: Mapped[str] = mapped_column(String(24), default="BAIXA", nullable=False)
    risk_level: Mapped[str] = mapped_column(String(24), default="NORMAL", nullable=False)
    accessibility_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    pcd_sos_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    equipments: Mapped[list["AccessibilityEquipmentModel"]] = relationship(
        "AccessibilityEquipmentModel",
        back_populates="station",
        cascade="all, delete-orphan",
    )
    telemetry_readings: Mapped[list["TelemetryReadingModel"]] = relationship(
        "TelemetryReadingModel",
        back_populates="station",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["CitizenAlertModel"]] = relationship(
        "CitizenAlertModel",
        back_populates="station",
        cascade="all, delete-orphan",
    )


class AccessibilityEquipmentModel(Base):
    """Equipamento de acessibilidade (Elevador PCD, Escada Rolante, Plataforma Elevatória)."""

    __tablename__ = "accessibility_equipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(40), nullable=False)
    location_description: Mapped[str] = mapped_column(String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="OPERANTE", nullable=False)
    last_maintenance_note: Mapped[str] = mapped_column(String(255), default="Inspeção preventiva em dia.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    station: Mapped["StationModel"] = relationship("StationModel", back_populates="equipments")


class TelemetryReadingModel(Base):
    """Histórico de leituras de telemetria enviadas pelos nós IoT (ESP32 Wokwi)."""

    __tablename__ = "telemetry_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_id: Mapped[str] = mapped_column(String(64), nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=False)
    heat_index_c: Mapped[float] = mapped_column(Float, nullable=False)
    distance_cm: Mapped[int] = mapped_column(Integer, nullable=False)
    occupancy_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    crowding_level: Mapped[str] = mapped_column(String(24), nullable=False)
    elevator_operational: Mapped[bool] = mapped_column(Boolean, nullable=False)
    escalator_operational: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pcd_sos_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(24), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)

    station: Mapped["StationModel"] = relationship("StationModel", back_populates="telemetry_readings")


class CitizenAlertModel(Base):
    """Alertas em tempo real emitidos por sensores IoT, predição ML ou relatos colaborativos de cidadãos."""

    __tablename__ = "citizen_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(24), default="WARNING", nullable=False)
    reported_by: Mapped[str] = mapped_column(String(80), default="SISTEMA_IOT_ESP32", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)

    station: Mapped["StationModel"] = relationship("StationModel", back_populates="alerts")
