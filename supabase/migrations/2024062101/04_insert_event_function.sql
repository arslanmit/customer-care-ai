-- Drop the function if it exists
DROP FUNCTION IF EXISTS rasa.insert_event(
    TEXT, TEXT, TEXT, TEXT, JSONB
);

-- Create the function with a simpler delimiter
CREATE OR REPLACE FUNCTION rasa.insert_event(
    p_sender_id TEXT,
    p_type_name TEXT,
    p_intent_name TEXT DEFAULT NULL,
    p_action_name TEXT DEFAULT NULL,
    p_data JSONB DEFAULT NULL
) 
RETURNS BIGINT 
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
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
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION rasa.insert_event(TEXT, TEXT, TEXT, TEXT, JSONB) TO authenticated;
