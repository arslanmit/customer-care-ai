import pytest
from typing import Dict, Text, Any, List
from unittest.mock import Mock
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet

class MockTracker(Tracker):
    """Mock tracker for testing slot extraction actions."""
    
    def __init__(self, slots: Dict[Text, Any] = None, 
                 latest_message: Dict[Text, Any] = None,
                 latest_event: Dict[Text, Any] = None):
        self._slots = slots or {}
        self.latest_message = latest_message or {}
        self.events = [latest_event] if latest_event else []
    
    def get_slot(self, key: Text) -> Any:
        return self._slots.get(key)
    
    def get_latest_entity_values(self, entity_type: Text) -> List[Text]:
        entities = self.latest_message.get("entities", [])
        return [
            entity["value"]
            for entity in entities
            if entity.get("entity") == entity_type
        ]

@pytest.fixture
def mock_dispatcher():
    """Create a mock dispatcher for testing."""
    dispatcher = Mock()
    dispatcher.utter_message = Mock()
    return dispatcher

@pytest.fixture
def mock_tracker():
    """Create a mock tracker for testing."""
    return MockTracker(slots={"some_slot": "some_value"})
