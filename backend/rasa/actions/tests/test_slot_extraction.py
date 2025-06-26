import pytest
from typing import Dict, Text, Any, List
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.action_extract_slots import (
    ActionExtractOrderNumber,
    ActionExtractProductId,
    ActionExtractEmail,
    ActionExtractPhoneNumber,
    ActionExtractDate,
    ActionExtractTime,
    ActionExtractLanguage,
    ActionExtractFirstName,
    ActionExtractLastName,
    ActionExtractComplaintType,
    ActionExtractComplaintDetails,
    ActionExtractCustomerEmail
)

# Test data
TEST_ORDER_NUMBER = "ORD12345"
TEST_PRODUCT_ID = "PROD67890"
TEST_EMAIL = "test@example.com"
TEST_PHONE = "+1234567890"
TEST_DATE = "2023-01-01"
TEST_TIME = "14:30"
TEST_LANGUAGE = "English"
TEST_FIRST_NAME = "John"
TEST_LAST_NAME = "Doe"
TEST_COMPLAINT_TYPE = "delivery"
TEST_COMPLAINT_DETAILS = "Package was damaged"

# Test cases as a list of tuples: (action_class, entity_type, slot_name, test_value)
TEST_CASES = [
    (ActionExtractOrderNumber, "order_number", "order_number", "ORD12345"),
    (ActionExtractProductId, "product_id", "product_id", "PROD67890"),
    (ActionExtractEmail, "email", "email", "test@example.com"),
    (ActionExtractPhoneNumber, "phone_number", "phone_number", "+1234567890"),
    (ActionExtractDate, "date", "requested_date", "2023-01-01"),
    (ActionExtractTime, "time", "requested_time", "14:30"),
    (ActionExtractLanguage, "language", "language", "English"),
    (ActionExtractFirstName, "first_name", "first_name", "John"),
    (ActionExtractLastName, "last_name", "last_name", "Doe"),
    (ActionExtractComplaintType, "complaint_type", "complaint_type", "delivery"),
    (ActionExtractComplaintDetails, "complaint_details", "complaint_details", "Package was damaged"),
    (ActionExtractCustomerEmail, "email", "customer_email", "customer@example.com"),
]

# Parametrized test for all slot extraction actions
@pytest.mark.parametrize("action_class,entity_type,slot_name,test_value", TEST_CASES)
def test_slot_extraction_actions(
    mock_dispatcher, action_class, entity_type, slot_name, test_value
):
    """Test slot extraction for all action types."""
    # Create a tracker with the test entity
    tracker = Tracker.from_dict({
        "sender_id": "test_user",
        "slots": {},
        "latest_message": {
            "intent": {"name": "test_intent", "confidence": 1.0},
            "entities": [
                {"entity": entity_type, "value": test_value, "extractor": "DIETClassifier"}
            ],
            "text": f"Test message with {entity_type} {test_value}",
        },
        "latest_event_time": 1620000000.0,
        "followup_action": None,
        "paused": False,
        "events": [],
        "latest_input_channel": "test",
        "active_loop": {},
        "latest_action_name": None,
    })
    
    action = action_class()
    events = action.run(mock_dispatcher, tracker, {})
    
    # Verify the correct slot was set
    assert len(events) == 1
    event = events[0]
    assert event["event"] == "slot"
    assert event["name"] == slot_name
    assert event["value"] == test_value

def test_no_entity_found(mock_dispatcher):
    """Test when no entity is found in the message."""
    # Create a tracker with no entities
    tracker = Tracker.from_dict({
        "sender_id": "test_user",
        "slots": {},
        "latest_message": {
            "intent": {"name": "test_intent", "confidence": 1.0},
            "entities": [],
            "text": "Test message with no entities",
        },
        "latest_event_time": 1620000000.0,
        "followup_action": None,
        "paused": False,
        "events": [],
        "latest_input_channel": "test",
        "active_loop": {},
        "latest_action_name": None,
    })
    
    action = ActionExtractOrderNumber()
    events = action.run(mock_dispatcher, tracker, {})
    
    # Should return an empty list when no entity is found
    assert events == []

def test_multiple_entities(mock_dispatcher):
    """Test that only the first matching entity is used."""
    # Create a tracker with multiple entities
    tracker = Tracker.from_dict({
        "sender_id": "test_user",
        "slots": {},
        "latest_message": {
            "intent": {"name": "test_intent", "confidence": 1.0},
            "entities": [
                {"entity": "order_number", "value": "FIRST123", "extractor": "DIETClassifier"},
                {"entity": "order_number", "value": "SECOND456", "extractor": "DIETClassifier"}
            ],
            "text": "Test message with multiple order numbers FIRST123 and SECOND456",
        },
        "latest_event_time": 1620000000.0,
        "followup_action": None,
        "paused": False,
        "events": [],
        "latest_input_channel": "test",
        "active_loop": {},
        "latest_action_name": None,
    })
    
    action = ActionExtractOrderNumber()
    events = action.run(mock_dispatcher, tracker, {})
    
    # Should only set the first matching entity
    assert len(events) == 1
    event = events[0]
    assert event["event"] == "slot"
    assert event["name"] == "order_number"
    assert event["value"] == "FIRST123"
