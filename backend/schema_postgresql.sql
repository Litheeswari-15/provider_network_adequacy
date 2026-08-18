-- ============================================================================
-- CARENET: PostgreSQL Database Schema & Ingestion Query
-- Primary Data Source: semantic_table.csv
-- ============================================================================

DROP TABLE IF EXISTS semantic_adequacy CASCADE;

CREATE TABLE semantic_adequacy (
    id SERIAL PRIMARY KEY,
    county VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    patient_count INTEGER NOT NULL DEFAULT 0,
    provider_count INTEGER NOT NULL DEFAULT 0,
    capacity_per_provider DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    total_capacity DECIMAL(12,2) NOT NULL DEFAULT 0.0,
    capacity_adequacy DECIMAL(6,2) NOT NULL DEFAULT 0.0,
    maximum_distance DECIMAL(6,2) NOT NULL DEFAULT 45.0,
    reasonable_patients INTEGER NOT NULL DEFAULT 0,
    distance_adequacy DECIMAL(6,2) NOT NULL DEFAULT 0.0,
    total_adequacy DECIMAL(6,2) NOT NULL DEFAULT 0.0,
    capacity_gap DECIMAL(6,2) NOT NULL DEFAULT 0.0,
    additional_providers_needed INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'PARTIALLY ADEQUATE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_semantic_location_specialty UNIQUE(county, city, specialty)
);

CREATE INDEX idx_semantic_lookup ON semantic_adequacy(county, city, specialty);
CREATE INDEX idx_semantic_county_city ON semantic_adequacy(county, city);
CREATE INDEX idx_semantic_specialty ON semantic_adequacy(specialty);

-- Load CSV directly into PostgreSQL:
-- Run this command in psql:
-- \copy semantic_adequacy(county, city, specialty, patient_count, provider_count, capacity_per_provider, total_capacity, capacity_adequacy, maximum_distance, reasonable_patients, distance_adequacy, total_adequacy, status) FROM 'data/semantic_table.csv' WITH (FORMAT csv, HEADER true);
