from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionIncrementFallbackCount(Action):
    """Increment the fallback counter and handle escalation if needed."""

    def name(self) -> Text:
        return "action_increment_fallback_count"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_fallbacks = tracker.get_slot("num_fallbacks") or 0
        return [SlotSet("num_fallbacks", current_fallbacks + 1)]
