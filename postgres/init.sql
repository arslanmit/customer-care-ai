-- Create database and user if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'rasa') THEN
        CREATE USER rasa WITH PASSWORD 'rasa123';
    END IF;
END
$$;

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE rasa'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rasa')\gexec

-- Connect to the database
\c rasa

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE rasa TO rasa;

-- Create schema
CREATE SCHEMA IF NOT EXISTS rasa AUTHORIZATION rasa;

-- Set search path
ALTER ROLE rasa IN DATABASE rasa SET search_path TO rasa, public;

-- Create tables
CREATE TABLE IF NOT EXISTS rasa.event (
    id SERIAL PRIMARY KEY,
    sender_id TEXT NOT NULL,
    type_name TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    intent_name TEXT,
    action_name TEXT,
    data JSONB
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_event_sender_id ON rasa.event(sender_id);
CREATE INDEX IF NOT EXISTS idx_event_timestamp ON rasa.event(timestamp);
CREATE INDEX IF NOT EXISTS idx_event_type ON rasa.event(type_name);

-- Grant permissions
GRANT USAGE ON SCHEMA rasa TO rasa;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA rasa TO rasa;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA rasa TO rasa;

-- Create function for event insertion
CREATE OR REPLACE FUNCTION rasa.insert_event(
    p_sender_id TEXT,
    p_type_name TEXT,
    p_intent_name TEXT DEFAULT NULL,
    p_action_name TEXT DEFAULT NULL,
    p_data JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    INSERT INTO rasa.event (
        sender_id,
        type_name,
        intent_name,
        action_name,
        data,
        timestamp
    ) VALUES (
        p_sender_id,
        p_type_name,
        p_intent_name,
        p_action_name,
        p_data,
        CURRENT_TIMESTAMP
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create view for conversation history
CREATE OR REPLACE VIEW rasa.conversation_history AS
SELECT 
    sender_id,
    timestamp,
    type_name,
    intent_name,
    action_name,
    data
FROM 
    rasa.event
ORDER BY 
    timestamp DESC;

-- Grant permissions on the view
GRANT SELECT ON rasa.conversation_history TO rasa;

-- Create a function to clean up old events
CREATE OR REPLACE FUNCTION rasa.cleanup_old_events(p_days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    v_rows_deleted INTEGER;
BEGIN
    DELETE FROM rasa.event
    WHERE timestamp < (CURRENT_TIMESTAMP - (p_days_to_keep * INTERVAL '1 day'));
    
    GET DIAGNOSTICS v_rows_deleted = ROW_COUNT;
    RETURN v_rows_deleted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a scheduled job to clean up old events
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'pg_cron'
    ) THEN
        CREATE EXTENSION pg_cron;
    END IF;
    
    -- Schedule cleanup to run daily at 2 AM
    PERFORM cron.schedule(
        'cleanup_old_events',
        '0 2 * * *',
        'SELECT rasa.cleanup_old_events(90)'
    );
EXCEPTION WHEN OTHERS THEN
    -- Extension might not be available, just log and continue
    RAISE NOTICE 'pg_cron extension not available: %', SQLERRM;
END
$$;
