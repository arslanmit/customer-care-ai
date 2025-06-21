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
