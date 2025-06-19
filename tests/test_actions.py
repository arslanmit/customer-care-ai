"""Unit tests for custom Rasa actions."""

import types
from pathlib import Path
import sys

# Ensure project root is on sys.path so that `actions` can be imported when tests
# are run from the project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the action under test
from actions.actions import ActionTellTime  # type: ignore


class DummyDispatcher:
    """A minimal dispatcher that records messages sent by the action."""

    def __init__(self):
        self.messages = []

    # The real dispatcher supports many params; we only need text for this test.
    def utter_message(self, text: str = None, **kwargs):  # noqa: D401,E501
        self.messages.append(text)


def test_action_tell_time():
    """ActionTellTime should send exactly one message mentioning the time."""

    action = ActionTellTime()
    dispatcher = DummyDispatcher()

    # tracker and domain are not used in this action; pass minimal stubs
    events = action.run(dispatcher=dispatcher, tracker=None, domain={})

    # The action should send exactly one response
    assert len(dispatcher.messages) == 1, "Expected exactly one bot message"

    response_text = dispatcher.messages[0] or ""
    assert "time" in response_text.lower(), "Response should mention time"

    # The action returns no events
    assert events == [], "Expected no events returned"
