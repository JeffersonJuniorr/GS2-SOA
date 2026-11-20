"""
Gerenciador de Migrações Versionadas do Banco de Dados (Database Migrations).
Registra e aplica migrações de schema de forma idempotente na tabela schema_migrations.
"""

from sqlalchemy.orm import Session
from app.infrastructure.database import Base, engine
from app.infrastructure.models import SchemaMigrationModel

MIGRATIONS = [
    (
        "V001__create_stations_table",
        "Criação da tabela de estações monitoradas (stations) com indicadores de lotação, clima e acessibilidade.",
    ),
    (
        "V002__create_accessibility_equipments_table",
        "Criação da tabela de equipamentos de acessibilidade (elevadores PCD, escadas rolantes e plataformas).",
    ),
    (
        "V003__create_telemetry_readings_table",
        "Criação da tabela de histórico de telemetria IoT (ESP32 Wokwi) com índices temporais.",
    ),
    (
        "V004__create_citizen_alerts_table",
        "Criação da tabela de alertas ao cidadão e ocorrências colaborativas de mobilidade.",
    ),
]


def run_migrations(db: Session) -> list[dict]:
    """
    Executa a criação/atualização do schema relacional e registra cada versão
    na tabela de auditoria `schema_migrations`.
    """
    Base.metadata.create_all(bind=engine)

    existing_versions = {
        row.version for row in db.query(SchemaMigrationModel).all()
    }

    applied = []
    for version, description in MIGRATIONS:
        if version not in existing_versions:
            migration = SchemaMigrationModel(version=version, description=description)
            db.add(migration)
            applied.append({"version": version, "description": description, "status": "APPLIED_NOW"})
        else:
            applied.append({"version": version, "description": description, "status": "ALREADY_APPLIED"})

    db.commit()
    return applied
