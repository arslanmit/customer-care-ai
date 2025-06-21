-- Enable RLS on the event table
ALTER TABLE rasa.event ENABLE ROW LEVEL SECURITY;

-- Drop existing policies first to avoid conflicts
DROP POLICY IF EXISTS "Enable read access for all users" ON rasa.event;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON rasa.event;

-- Create read policy
CREATE POLICY "Enable read access for all users" 
ON rasa.event FOR SELECT 
USING (true);

-- Create insert policy
CREATE POLICY "Enable insert for authenticated users only"
ON rasa.event FOR INSERT 
TO authenticated
WITH CHECK (true);

-- Grant necessary permissions
GRANT SELECT, INSERT ON rasa.event TO authenticated;
GRANT SELECT ON rasa.event TO anon;
