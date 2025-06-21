-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS rasa;

-- Create table if it doesn't exist
CREATE TABLE IF NOT EXISTS rasa.event (
    id BIGSERIAL PRIMARY KEY,
    sender_id TEXT NOT NULL,
    type_name TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    intent_name TEXT,
    action_name TEXT,
    data JSONB
);

-- Create indexes if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'rasa' AND tablename = 'event' AND indexname = 'idx_event_sender_id') THEN
        CREATE INDEX idx_event_sender_id ON rasa.event(sender_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'rasa' AND tablename = 'event' AND indexname = 'idx_event_timestamp') THEN
        CREATE INDEX idx_event_timestamp ON rasa.event(timestamp);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'rasa' AND tablename = 'event' AND indexname = 'idx_event_type') THEN
        CREATE INDEX idx_event_type ON rasa.event(type_name);
    END IF;
END $$;

-- Enable RLS if not already enabled
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_tables 
        WHERE schemaname = 'rasa' 
          AND tablename = 'event' 
          AND rowsecurity = true
    ) THEN
        ALTER TABLE rasa.event ENABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- Create policies if they don't exist
DO $$
BEGIN
    -- Check if read policy exists
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_policy p 
        JOIN pg_class c ON p.polrelid = c.oid 
        JOIN pg_namespace n ON c.relnamespace = n.oid 
        WHERE n.nspname = 'rasa' 
          AND c.relname = 'event' 
          AND p.polname = 'Enable read access for all users'
    ) THEN
        CREATE POLICY "Enable read access for all users" 
        ON rasa.event FOR SELECT 
        USING (true);
    END IF;
    
    -- Check if insert policy exists
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_policy p 
        JOIN pg_class c ON p.polrelid = c.oid 
        JOIN pg_namespace n ON c.relnamespace = n.oid 
        WHERE n.nspname = 'rasa' 
          AND c.relname = 'event' 
          AND p.polname = 'Enable insert for authenticated users only'
    ) THEN
        CREATE POLICY "Enable insert for authenticated users only"
        ON rasa.event FOR INSERT 
        TO authenticated
        WITH CHECK (true);
    END IF;
END $$;

-- Create or replace function for event insertion
DO $$
BEGIN
    -- Drop function if it exists
    IF EXISTS (
        SELECT 1 
        FROM pg_proc p 
        JOIN pg_namespace n ON p.pronamespace = n.oid 
        WHERE n.nspname = 'rasa' 
        AND p.proname = 'insert_event'
    ) THEN
        DROP FUNCTION rasa.insert_event(
            TEXT, TEXT, TEXT, TEXT, JSONB
        );
    END IF;
    
    -- Create the function
    CREATE FUNCTION rasa.insert_event(
        p_sender_id TEXT,
        p_type_name TEXT,
        p_intent_name TEXT DEFAULT NULL,
        p_action_name TEXT DEFAULT NULL,
        p_data JSONB DEFAULT NULL
    ) 
    RETURNS BIGINT 
    SECURITY DEFINER
    AS $func$
    DECLARE
        v_id BIGINT;
    BEGIN
        INSERT INTO rasa.event (
            sender_id,
            type_name,
            intent_name,
            action_name,
            data
        ) VALUES (
            p_sender_id,
            p_type_name,
            p_intent_name,
            p_action_name,
            p_data
        )
        RETURNING id INTO v_id;
        
        RETURN v_id;
    END;
    $func$ LANGUAGE plpgsql;
END $$;

-- Create or replace view for conversation history
DO $$
BEGIN
    -- Drop the view if it exists
    IF EXISTS (
        SELECT 1 
        FROM pg_views 
        WHERE schemaname = 'rasa' 
        AND viewname = 'conversation_history'
    ) THEN
        DROP VIEW rasa.conversation_history;
    END IF;
    
    -- Create the view
    CREATE VIEW rasa.conversation_history AS
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
        
    -- Grant permissions
    GRANT SELECT ON rasa.conversation_history TO authenticated, anon;
END $$;

-- Create or replace cleanup function
DO $$
BEGIN
    -- Drop the function if it exists
    IF EXISTS (
        SELECT 1 
        FROM pg_proc p 
        JOIN pg_namespace n ON p.pronamespace = n.oid 
        WHERE n.nspname = 'rasa' 
        AND p.proname = 'cleanup_old_events'
    ) THEN
        DROP FUNCTION rasa.cleanup_old_events();
    END IF;
    
    -- Create the function
    CREATE FUNCTION rasa.cleanup_old_events()
    RETURNS TRIGGER 
    AS $cleanup$
    BEGIN
        DELETE FROM rasa.event 
        WHERE timestamp < (CURRENT_TIMESTAMP - INTERVAL '30 days');
        RETURN NULL;
    END;
    $cleanup$ LANGUAGE plpgsql;
    
    -- Grant execute permission
    GRANT EXECUTE ON FUNCTION rasa.cleanup_old_events() TO authenticated;
END $$;

-- Create or replace trigger for cleanup
DO $$
BEGIN
    -- Drop the trigger if it exists
    IF EXISTS (
        SELECT 1 
        FROM pg_trigger t 
        JOIN pg_class c ON t.tgrelid = c.oid 
        JOIN pg_namespace n ON c.relnamespace = n.oid 
        WHERE n.nspname = 'rasa' 
        AND c.relname = 'event' 
        AND t.tgname = 'trigger_cleanup_old_events'
    ) THEN
        DROP TRIGGER IF EXISTS trigger_cleanup_old_events ON rasa.event;
    END IF;
    
    -- Create the trigger
    CREATE TRIGGER trigger_cleanup_old_events
    AFTER INSERT ON rasa.event
    EXECUTE FUNCTION rasa.cleanup_old_events();
    
    -- Grant permission
    ALTER TABLE rasa.event ENABLE ALWAYS TRIGGER trigger_cleanup_old_events;
END $$;
