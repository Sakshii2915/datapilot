-- ====================================================================
-- DataPilot: Read-Only User Setup (PostgreSQL Security Layer)
-- ====================================================================

-- 1. Create dedicated read-only role and user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'datapilot_ro') THEN
        CREATE ROLE datapilot_ro WITH LOGIN PASSWORD 'datapilot_ro_pass';
    END IF;
END
$$;

-- 2. Grant connection and schema access
GRANT CONNECT ON DATABASE datapilot TO datapilot_ro;
GRANT USAGE ON SCHEMA public TO datapilot_ro;

-- 3. Grant SELECT only on all analytics tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO datapilot_ro;

-- 4. Automatically grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO datapilot_ro;

-- 5. Explicitly revoke any modification permissions
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA public FROM datapilot_ro;
REVOKE CREATE ON SCHEMA public FROM datapilot_ro;
