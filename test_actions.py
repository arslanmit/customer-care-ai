"""
Test script to verify Rasa custom actions.
"""
import os
import sys
import asyncio
from typing import Dict, Any, Text, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Add the actions directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the action we want to test
from actions.actions import ActionTellTime


class MockTracker:
    """Mock tracker for testing Rasa actions."""
    
    def __init__(self, slots: Dict[Text, Any] = None):
        """Initialize mock tracker with optional slots."""
        self.slots = slots or {}
    
    def get_slot(self, key: Text) -> Any:
        """Get a slot value."""
        return self.slots.get(key)


class MockDispatcher:
    """Mock dispatcher for testing Rasa actions."""
    
    def __init__(self):
        """Initialize mock dispatcher."""
        self.messages = []
    
    def utter_message(self, text: Text = None, **kwargs):
        """Capture messages sent by actions."""
        self.messages.append({"text": text, **kwargs})
    
    def get_messages(self) -> List[Dict[Text, Any]]:
        """Get all captured messages."""
        return self.messages


async def test_action_tell_time() -> bool:
    """Test the ActionTellTime action."""
    print("Testing ActionTellTime...")
    
    # Setup test components
    dispatcher = MockDispatcher()
    tracker = MockTracker()
    domain = {}
    
    # Create and run the action
    action = ActionTellTime()
    events = await action.run(dispatcher, tracker, domain)
    
    # Verify results
    messages = dispatcher.get_messages()
    
    if not messages:
        print("❌ Test failed: No messages were sent by the action")
        return False
    
    if len(messages) != 1:
        print(f"❌ Test failed: Expected 1 message, got {len(messages)}")
        return False
    
    message = messages[0]
    if "text" not in message or not message["text"].startswith("The current time is"):
        print(f"❌ Test failed: Unexpected message content: {message}")
        return False
    
    print("✅ ActionTellTime test passed!")
    print(f"Message: {message['text']}")
    return True


async def main():
    """Run all tests."""
    print("Starting Rasa actions tests...\n")
    
    # Run tests
    tests = [
        test_action_tell_time,
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()  # Add a newline between tests
    
    # Print summary
    print("\nTest Summary:")
    print("============")
    for i, result in enumerate(results, 1):
        status = "PASSED" if result else "FAILED"
        print(f"Test {i}: {status}")
    
    # Exit with appropriate status code
    if all(results):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
