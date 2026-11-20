-- ============================================================================
-- MIGRATION V003 & V004: Tabelas de Telemetria IoT (ESP32) e Alertas Cidadãos
-- ============================================================================

CREATE TABLE IF NOT EXISTS telemetry_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id INTEGER NOT NULL,
    node_id VARCHAR(64) NOT NULL,
    temperature_c FLOAT NOT NULL,
    humidity_pct FLOAT NOT NULL,
    heat_index_c FLOAT NOT NULL,
    distance_cm INTEGER NOT NULL,
    occupancy_pct INTEGER NOT NULL,
    crowding_level VARCHAR(24) NOT NULL,
    elevator_operational BOOLEAN NOT NULL,
    escalator_operational BOOLEAN NOT NULL,
    pcd_sos_active BOOLEAN NOT NULL DEFAULT 0,
    risk_level VARCHAR(24) NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_telemetry_station FOREIGN KEY (station_id) REFERENCES stations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_telemetry_readings_station_id ON telemetry_readings (station_id);
CREATE INDEX IF NOT EXISTS ix_telemetry_readings_recorded_at ON telemetry_readings (recorded_at);

CREATE TABLE IF NOT EXISTS citizen_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    severity VARCHAR(24) NOT NULL DEFAULT 'WARNING',
    reported_by VARCHAR(80) NOT NULL DEFAULT 'SISTEMA_IOT_ESP32',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alerts_station FOREIGN KEY (station_id) REFERENCES stations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_citizen_alerts_station_id ON citizen_alerts (station_id);
