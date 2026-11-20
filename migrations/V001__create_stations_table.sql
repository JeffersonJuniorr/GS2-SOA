-- ============================================================================
-- MIGRATION V001: Criação da Tabela de Estações e Controle de Migrações
-- Projeto: CitizenTech Deslocai (SOA & Web Services - FIAP 2026)
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(64) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    line_name VARCHAR(80) NOT NULL,
    transport_mode VARCHAR(32) NOT NULL,
    district VARCHAR(80) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    daily_passengers_avg INTEGER NOT NULL DEFAULT 50000,
    current_occupancy_pct INTEGER NOT NULL DEFAULT 30,
    current_temperature_c FLOAT NOT NULL DEFAULT 25.0,
    current_humidity_pct FLOAT NOT NULL DEFAULT 60.0,
    current_heat_index_c FLOAT NOT NULL DEFAULT 25.0,
    crowding_level VARCHAR(24) NOT NULL DEFAULT 'BAIXA',
    risk_level VARCHAR(24) NOT NULL DEFAULT 'NORMAL',
    accessibility_score INTEGER NOT NULL DEFAULT 100,
    pcd_sos_active BOOLEAN NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_stations_code ON stations (code);
