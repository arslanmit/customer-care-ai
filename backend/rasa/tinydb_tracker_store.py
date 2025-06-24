"""
TinyDB Tracker Store for Rasa Core

This module provides a TinyDB implementation of Rasa's TrackerStore that
persists conversation trackers in a local JSON file.
"""

import logging
import os.path
import threading
from typing import Any, Dict, Optional, Text

from rasa.core.tracker_store import TrackerStore
from rasa.shared.core.trackers import DialogueStateTracker, EventVerbosity
from tinydb import Query, TinyDB

logger = logging.getLogger(__name__)


class TinyDBTrackerStore(TrackerStore):
    """TinyDB-based tracker store for conversation history persistence.

    Stores conversation trackers in a local JSON file powered by TinyDB.
    Uses a lock mechanism to allow for thread-safety when accessing the database.
    """

    def __init__(
        self,
        domain,
        db_path: Text = "data/rasa_conversations.json",
        **kwargs: Dict[Text, Any],
    ) -> None:
        """Initialize the TinyDB tracker store.

        Args:
            domain: Domain instance
            db_path: Path to the TinyDB JSON file
            **kwargs: Additional arguments passed to the TrackerStore
        """
        super().__init__(domain, **kwargs)

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self.db_path = db_path
        # Use JSONStorage directly with indent=2 for pretty printing
        from tinydb.storages import JSONStorage

        self.db = TinyDB(db_path, storage=lambda fp: JSONStorage(fp, indent=2))
        print(f"[TinyDBTrackerStore] Initialized with db_path={db_path}")
        logger.debug(f"[TinyDBTrackerStore] Initialized with db_path={db_path}")

        # Create a lock for thread-safe operations
        self.lock = threading.Lock()

        logger.debug(f"Initialized TinyDBTrackerStore with db_path={db_path}")
        print("[TinyDBTrackerStore] Initialized with db_path=", db_path)

    def save(self, tracker: DialogueStateTracker) -> None:
        """Save the conversation tracker to TinyDB.

        This will atomically:
        1. Remove any existing tracker with the same sender_id
        2. Insert the new tracker as a serialized dict

        Args:
            tracker: The dialogue tracker to save
        """
        sender_id = tracker.sender_id
        print(f"[TinyDBTrackerStore] save() called for sender_id={sender_id}")
        logger.debug(f"[TinyDBTrackerStore] save() called for sender_id={sender_id}")
        serialized_tracker = tracker.current_state(event_verbosity=EventVerbosity.ALL)
        try:
            with self.lock:
                # Remove existing entries for this sender
                User = Query()
                self.db.remove(User.sender_id == sender_id)
                self.db.insert(serialized_tracker)
            logger.debug(f"Saved tracker for sender_id={sender_id} to TinyDB")
            print(
                f"[TinyDBTrackerStore] Saved tracker for sender_id={sender_id} "
                f"to TinyDB"
            )
        except Exception as e:
            logger.error(f"TinyDBTrackerStore save error: {e}")
            print(f"[TinyDBTrackerStore] ERROR during save: {e}")

    def retrieve(self, sender_id: Text) -> Optional[DialogueStateTracker]:
        """Retrieve a specific tracker from TinyDB.

        Args:
            sender_id: The sender ID to retrieve the tracker for

        Returns:
            A reconstructed DialogueStateTracker or None if not found
        """
        # Use mutex to ensure only one thread accesses the DB at a time
        with self.lock:
            User = Query()
            result = self.db.search(User.sender_id == sender_id)

        if not result:
            # No tracker exists for this sender_id
            logger.debug(f"No tracker found for sender_id={sender_id}")
            return None

        # The result is a list of matching documents, but we expect only one
        serialized = result[0]

        # Create a new tracker with events from the persisted state
        tracker = DialogueStateTracker.from_dict(
            sender_id, serialized.get("events", []), self.domain.slots
        )

        logger.debug(f"Retrieved and reconstructed tracker for sender_id={sender_id}")
        return tracker

    def keys(self):
        """Return a list of all sender_ids in the store."""
        all_trackers = self.db.all()
        return [
            tracker.get("sender_id")
            for tracker in all_trackers
            if "sender_id" in tracker
        ]
