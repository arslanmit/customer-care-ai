-- Drop the view if it exists
DROP VIEW IF EXISTS rasa.conversation_history;

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
