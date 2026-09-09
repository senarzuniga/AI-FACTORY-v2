-- =============================================================================
-- Ingetrans System Parameters Schema
-- =============================================================================
-- Tables for storing validated Ingetrans system technical specifications
-- Run this script in your database to create the necessary tables
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Systems Table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingetrans_systems (
    system_id           TEXT PRIMARY KEY,
    system_name         TEXT NOT NULL,
    system_description  TEXT,
    system_type         TEXT NOT NULL,
    version             TEXT NOT NULL,
    validation_status   TEXT NOT NULL DEFAULT 'pending',
    approval_status     TEXT NOT NULL DEFAULT 'pending',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          TEXT,
    approved_by         TEXT
);

CREATE INDEX IF NOT EXISTS idx_ingetrans_systems_validation_status 
    ON ingetrans_systems (validation_status);
CREATE INDEX IF NOT EXISTS idx_ingetrans_systems_approval_status 
    ON ingetrans_systems (approval_status);

COMMENT ON TABLE ingetrans_systems IS 
    'Ingetrans rail-guided transfer carriage system definitions';

-- ---------------------------------------------------------------------------
-- System Parameters Table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingetrans_parameters (
    parameter_id        TEXT PRIMARY KEY,
    system_id           TEXT NOT NULL REFERENCES ingetrans_systems (system_id) ON DELETE CASCADE,
    parameter_name      TEXT NOT NULL,
    parameter_type      TEXT NOT NULL,
    unit                TEXT,
    value_min           NUMERIC(10, 2),
    value_max           NUMERIC(10, 2),
    value_nominal       NUMERIC(10, 2),
    description         TEXT,
    notes               TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ingetrans_parameters_system_id 
    ON ingetrans_parameters (system_id);
CREATE INDEX IF NOT EXISTS idx_ingetrans_parameters_name 
    ON ingetrans_parameters (parameter_name);

COMMENT ON TABLE ingetrans_parameters IS 
    'Technical parameters for Ingetrans systems (transfer speed, track speed, etc.)';

-- ---------------------------------------------------------------------------
-- Safety Requirements Table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingetrans_safety_requirements (
    safety_id           TEXT PRIMARY KEY,
    system_id           TEXT NOT NULL REFERENCES ingetrans_systems (system_id) ON DELETE CASCADE,
    requirement_name    TEXT NOT NULL,
    requirement_type    TEXT NOT NULL,
    description         TEXT,
    compliance_standard TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ingetrans_safety_system_id 
    ON ingetrans_safety_requirements (system_id);

COMMENT ON TABLE ingetrans_safety_requirements IS 
    'Safety requirements and compliance standards for Ingetrans systems';

-- ---------------------------------------------------------------------------
-- Control Systems Table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingetrans_control_systems (
    control_id          TEXT PRIMARY KEY,
    system_id           TEXT NOT NULL REFERENCES ingetrans_systems (system_id) ON DELETE CASCADE,
    architecture        TEXT NOT NULL,
    communication_type  TEXT NOT NULL,
    interface_signals   TEXT,
    plc_type            TEXT,
    hmi_type            TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ingetrans_control_system_id 
    ON ingetrans_control_systems (system_id);

COMMENT ON TABLE ingetrans_control_systems IS 
    'Control system specifications (PLC, HMI, PROFINET, interface signals)';

-- ---------------------------------------------------------------------------
-- Data Validation Log Table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingetrans_validation_log (
    log_id              TEXT PRIMARY KEY,
    system_id           TEXT NOT NULL REFERENCES ingetrans_systems (system_id) ON DELETE CASCADE,
    validation_type     TEXT NOT NULL,
    validation_status   TEXT NOT NULL,
    error_messages      TEXT,
    validated_by        TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ingetrans_validation_log_system_id 
    ON ingetrans_validation_log (system_id);
CREATE INDEX IF NOT EXISTS idx_ingetrans_validation_log_status 
    ON ingetrans_validation_log (validation_status);

COMMENT ON TABLE ingetrans_validation_log IS 
    'Audit trail for data validation and corrections in Ingetrans systems';

-- ---------------------------------------------------------------------------
-- Insert validated Ingetrans system data
-- ---------------------------------------------------------------------------
INSERT INTO ingetrans_systems (
    system_id,
    system_name,
    system_description,
    system_type,
    version,
    validation_status,
    approval_status,
    created_by,
    approved_by
) VALUES (
    'ingetrans-001',
    'Ingetrans',
    'Rail-guided transfer carriage system with dedicated fixed reel tracks',
    'Surface rail-guided transfer carriage',
    '1.0.0',
    'validated',
    'approved',
    'Engineering Department',
    'Engineering Department'
) ON CONFLICT DO NOTHING;

-- Insert transfer speed parameter
INSERT INTO ingetrans_parameters (
    parameter_id,
    system_id,
    parameter_name,
    parameter_type,
    unit,
    value_min,
    value_max,
    value_nominal,
    description,
    notes,
    status
) VALUES (
    'ingetrans-param-transfer-speed',
    'ingetrans-001',
    'Transfer speed',
    'numeric_range',
    'm/min',
    80,
    100,
    90,
    'Speed of rail-guided transfer carriage',
    'Final value subject to approved layout and safety zones',
    'active'
) ON CONFLICT DO NOTHING;

-- Insert track speed parameter
INSERT INTO ingetrans_parameters (
    parameter_id,
    system_id,
    parameter_name,
    parameter_type,
    unit,
    value_min,
    value_max,
    value_nominal,
    description,
    notes,
    status
) VALUES (
    'ingetrans-param-track-speed',
    'ingetrans-001',
    'Track speed',
    'numeric_range',
    'm/min',
    12,
    19,
    15.5,
    'Speed of fixed reel tracks',
    'Rail movement speed reference value',
    'active'
) ON CONFLICT DO NOTHING;

-- Insert acceleration/deceleration parameter
INSERT INTO ingetrans_parameters (
    parameter_id,
    system_id,
    parameter_name,
    parameter_type,
    unit,
    value_nominal,
    description,
    notes,
    status
) VALUES (
    'ingetrans-param-accel-decel',
    'ingetrans-001',
    'Acceleration/deceleration',
    'numeric',
    'seconds',
    1.5,
    'Ramp time for acceleration and deceleration',
    'Time to reach nominal speed from stop',
    'active'
) ON CONFLICT DO NOTHING;

-- Insert pickup/drop-off parameter
INSERT INTO ingetrans_parameters (
    parameter_id,
    system_id,
    parameter_name,
    parameter_type,
    unit,
    value_nominal,
    description,
    notes,
    status
) VALUES (
    'ingetrans-param-pickup-dropoff',
    'ingetrans-001',
    'Pickup/drop-off',
    'numeric',
    'seconds per interface',
    6,
    'Transfer action time per interface',
    'Time required for each pickup or dropoff operation',
    'active'
) ON CONFLICT DO NOTHING;

-- Insert reel envelope parameters
INSERT INTO ingetrans_parameters (
    parameter_id,
    system_id,
    parameter_name,
    parameter_type,
    unit,
    value_max,
    description,
    notes,
    status
) VALUES (
    'ingetrans-param-reel-diameter',
    'ingetrans-001',
    'Reel envelope - Diameter',
    'numeric',
    'mm',
    1500,
    'Maximum reel diameter',
    'Subject to final approved reel matrix',
    'active'
) ON CONFLICT DO NOTHING;

INSERT INTO ingetrans_parameters (
    parameter_id,
    system_id,
    parameter_name,
    parameter_type,
    unit,
    value_max,
    description,
    notes,
    status
) VALUES (
    'ingetrans-param-reel-width',
    'ingetrans-001',
    'Reel envelope - Width/Length',
    'numeric',
    'mm',
    2800,
    'Maximum reel width/length',
    'Subject to final approved reel matrix',
    'active'
) ON CONFLICT DO NOTHING;

INSERT INTO ingetrans_parameters (
    parameter_id,
    system_id,
    parameter_name,
    parameter_type,
    unit,
    value_max,
    description,
    notes,
    status
) VALUES (
    'ingetrans-param-reel-weight',
    'ingetrans-001',
    'Reel envelope - Weight',
    'numeric',
    'kg',
    3500,
    'Maximum reel weight',
    'Subject to final approved reel matrix',
    'active'
) ON CONFLICT DO NOTHING;

-- Insert control system
INSERT INTO ingetrans_control_systems (
    control_id,
    system_id,
    architecture,
    communication_type,
    interface_signals,
    plc_type,
    hmi_type,
    status
) VALUES (
    'ingetrans-control-001',
    'ingetrans-001',
    'Industrial PLC/HMI architecture',
    'PROFINET/industrial communications',
    'Defined during engineering',
    'Industrial PLC',
    'Industrial HMI',
    'active'
) ON CONFLICT DO NOTHING;

-- Insert safety requirements
INSERT INTO ingetrans_safety_requirements (
    safety_id,
    system_id,
    requirement_name,
    requirement_type,
    description,
    compliance_standard,
    status
) VALUES (
    'ingetrans-safety-pmc',
    'ingetrans-001',
    'Safety PLC functions',
    'control_safety',
    'Programmable Logic Controller with safety-rated functions',
    'ISO 13849-1',
    'active'
) ON CONFLICT DO NOTHING;

INSERT INTO ingetrans_safety_requirements (
    safety_id,
    system_id,
    requirement_name,
    requirement_type,
    description,
    compliance_standard,
    status
) VALUES (
    'ingetrans-safety-scanners',
    'ingetrans-001',
    'Area scanners',
    'monitoring',
    'Safety scanners for personnel and obstacle detection',
    'ISO 13849-1',
    'active'
) ON CONFLICT DO NOTHING;

INSERT INTO ingetrans_safety_requirements (
    safety_id,
    system_id,
    requirement_name,
    requirement_type,
    description,
    compliance_standard,
    status
) VALUES (
    'ingetrans-safety-interlocks',
    'ingetrans-001',
    'Interlocks',
    'access_control',
    'Safety interlocks on access points',
    'ISO 13849-1',
    'active'
) ON CONFLICT DO NOTHING;

INSERT INTO ingetrans_safety_requirements (
    safety_id,
    system_id,
    requirement_name,
    requirement_type,
    description,
    compliance_standard,
    status
) VALUES (
    'ingetrans-safety-estop',
    'ingetrans-001',
    'Emergency stops',
    'emergency_control',
    'Emergency stop buttons for immediate system shutdown',
    'ISO 13850',
    'active'
) ON CONFLICT DO NOTHING;

INSERT INTO ingetrans_safety_requirements (
    safety_id,
    system_id,
    requirement_name,
    requirement_type,
    description,
    compliance_standard,
    status
) VALUES (
    'ingetrans-safety-access',
    'ingetrans-001',
    'Protected access',
    'physical_security',
    'Physical barriers and controlled access to operational areas',
    'ISO 13849-1',
    'active'
) ON CONFLICT DO NOTHING;
