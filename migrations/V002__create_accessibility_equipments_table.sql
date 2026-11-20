-- ============================================================================
-- MIGRATION V002: Criação da Tabela de Equipamentos de Acessibilidade (PCD)
-- ============================================================================

CREATE TABLE IF NOT EXISTS accessibility_equipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id INTEGER NOT NULL,
    code VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    equipment_type VARCHAR(40) NOT NULL,
    location_description VARCHAR(180) NOT NULL,
    status VARCHAR(24) NOT NULL DEFAULT 'OPERANTE',
    last_maintenance_note VARCHAR(255) NOT NULL DEFAULT 'Inspeção preventiva em dia.',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_equip_station FOREIGN KEY (station_id) REFERENCES stations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_accessibility_equipments_station_id ON accessibility_equipments (station_id);
CREATE INDEX IF NOT EXISTS ix_accessibility_equipments_code ON accessibility_equipments (code);
