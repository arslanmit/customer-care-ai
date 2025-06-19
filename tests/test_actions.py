"""Unit tests for custom Rasa actions."""

import types
from pathlib import Path
import sys

# Ensure project root is on sys.path so that `actions` can be imported when tests
# are run from the project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Provide a lightweight stub for rasa_sdk if it's not installed
try:
    import rasa_sdk  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import types

    rasa_sdk = types.ModuleType("rasa_sdk")
    sys.modules["rasa_sdk"] = rasa_sdk

    class _StubAction:  # pylint: disable=too-few-public-methods
        def name(self):
            return "stub_action"

        def run(self, *args, **kwargs):  # noqa: D401
            return []

    class _StubTracker:  # pylint: disable=too-few-public-methods
        pass

    class _StubDispatcher:  # pylint: disable=too-few-public-methods
        def utter_message(self, **_: str):  # noqa: D401
            pass

    rasa_sdk.Action = _StubAction  # type: ignore
    rasa_sdk.Tracker = _StubTracker  # type: ignore
    rasa_sdk.CollectingDispatcher = _StubDispatcher  # type: ignore

    # create executor submodule with CollectingDispatcher
    executor_module = types.ModuleType("rasa_sdk.executor")
    executor_module.CollectingDispatcher = _StubDispatcher  # type: ignore
    sys.modules["rasa_sdk.executor"] = executor_module

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
