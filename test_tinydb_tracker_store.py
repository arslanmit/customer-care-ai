"""
Test script for TinyDBTrackerStore

This script creates a dummy Rasa domain, saves a tracker, retrieves it, and prints the results.
Run this to verify that TinyDBTrackerStore works independently of Rasa server.
"""
import os
import threading
from pathlib import Path

from rasa.shared.core.domain import Domain
from rasa.shared.core.events import UserUttered, BotUttered
from rasa.shared.core.trackers import DialogueStateTracker

from tinydb_tracker_store import TinyDBTrackerStore

def main():
    # Setup dummy domain
    domain = Domain.empty()
    sender_id = "test_user"
    db_path = "data/test_rasa_conversations.json"
    
    # Remove old test db if exists
    if Path(db_path).exists():
        os.remove(db_path)
    
    # Create tracker store
    store = TinyDBTrackerStore(domain, db_path=db_path)
    
    # Create a tracker with some events
    tracker = DialogueStateTracker(sender_id, slots=domain.slots)
    tracker.update(UserUttered(text="hello", intent={"name": "greet", "confidence": 1.0}))
    tracker.update(BotUttered(text="Hi there!"))
    
    # Save tracker
    store.save(tracker)
    print("Tracker saved.")
    
    # Retrieve tracker
    loaded = store.retrieve(sender_id)
    print("Retrieved tracker:")
    print(f"Events: {[e.as_dict() for e in loaded.events]}")
    
    # Check that the events match
    assert len(loaded.events) == 2, "Event count mismatch!"
    assert loaded.events[0].as_dict()["event"] == "user", "First event should be user utterance"
    assert loaded.events[1].as_dict()["event"] == "bot", "Second event should be bot utterance"
    print("Test passed!")

if __name__ == "__main__":
    main()
