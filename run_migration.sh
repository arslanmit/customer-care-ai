#!/bin/bash

#!/bin/bash

# Exit on error
set -e

# Check if migration.env exists
if [ ! -f "migration.env" ]; then
    echo "Error: migration.env file not found."
    echo "Please create it by copying migration.env.example and updating with your database credentials."
    exit 1
fi

# Load environment variables
echo "Loading database configuration from migration.env..."
source migration.env

# Check if required environment variable is set
if [ -z "$SUPABASE_DB_URL" ]; then
    echo "Error: SUPABASE_DB_URL is not set in migration.env"
    exit 1
fi

# Run the migration script
echo "Starting database migrations..."
python scripts/apply_supabase_schema.py

echo "Migrations completed successfully!"
