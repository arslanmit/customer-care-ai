"""
Export Supabase conversation events to a local JSON file

This script exports all conversation events from Supabase to a local JSON file for use
with the FileEventBroker. Run this once before switching to the FileEventBroker.

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) env vars.
"""
import os
import json
import logging
from pathlib import Path

try:
    from supabase import create_client
except ImportError:
    print("Error: supabase-py not installed. Run: pip install supabase")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get Supabase credentials from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    logger.error("Missing environment variables: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY)")
    exit(1)

# Initialize Supabase client
supabase = create_client(supabase_url, supabase_key)

# Target file
output_file = Path("data/events.json")
os.makedirs(output_file.parent, exist_ok=True)

def export_events():
    """Export events from Supabase to a local JSON file."""
    try:
        # Fetch all events from the conversation_events table
        response = supabase.table("conversation_events").select("*").execute()
        
        events = response.data
        logger.info(f"Retrieved {len(events)} events from Supabase")
        
        # Check if we have events to export
        if not events:
            logger.warning("No events found in Supabase")
            return
        
        # If the file exists, read existing content first
        existing_events = []
        if output_file.exists() and output_file.stat().st_size > 0:
            try:
                with open(output_file, "r") as f:
                    existing_events = json.load(f)
                    if not isinstance(existing_events, list):
                        existing_events = []
                logger.info(f"Read {len(existing_events)} existing events from {output_file}")
            except json.JSONDecodeError:
                logger.warning(f"Could not parse existing file {output_file}, will overwrite")
        
        # Combine events (avoiding duplicates based on some unique identifier)
        # Modify this logic according to your event structure
        combined_events = existing_events.copy()
        new_count = 0
        
        # This assumes events have some unique identifier like 'id'
        existing_ids = {event.get('id') for event in existing_events if 'id' in event}
        
        for event in events:
            if 'id' in event and event['id'] not in existing_ids:
                combined_events.append(event)
                new_count += 1
        
        # Write all events to the file
        with open(output_file, "w") as f:
            json.dump(combined_events, f, indent=2)
        
        logger.info(f"Successfully exported {len(combined_events)} events to {output_file} ({new_count} new)")
        
    except Exception as e:
        logger.error(f"Error exporting events: {e}")
        raise

if __name__ == "__main__":
    export_events()
    logger.info("Export completed")
