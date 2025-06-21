-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_event_sender_id ON rasa.event(sender_id);
CREATE INDEX IF NOT EXISTS idx_event_timestamp ON rasa.event(timestamp);
CREATE INDEX IF NOT EXISTS idx_event_type ON rasa.event(type_name);
