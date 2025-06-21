-- Drop the trigger first if it exists
DROP TRIGGER IF EXISTS trigger_cleanup_old_events ON rasa.event;

-- Drop the function if it exists with CASCADE to handle any dependencies
DROP FUNCTION IF EXISTS rasa.cleanup_old_events() CASCADE;

-- Create the cleanup function
CREATE OR REPLACE FUNCTION rasa.cleanup_old_events()
RETURNS TRIGGER
AS $cleanup$
BEGIN
    -- Delete events older than 30 days
    DELETE FROM rasa.event
    WHERE timestamp < NOW() - INTERVAL '30 days';
    RETURN NULL;
END;
$cleanup$ LANGUAGE plpgsql;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION rasa.cleanup_old_events() TO authenticated;

-- Recreate the trigger
CREATE TRIGGER trigger_cleanup_old_events
AFTER INSERT ON rasa.event
EXECUTE FUNCTION rasa.cleanup_old_events();

-- Enable the trigger
ALTER TABLE rasa.event ENABLE ALWAYS TRIGGER trigger_cleanup_old_events;
