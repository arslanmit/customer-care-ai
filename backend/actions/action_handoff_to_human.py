from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionHandoffToHuman(Action):
    """Handle the handoff to a human agent."""

    def name(self) -> Text:
        return "action_handoff_to_human"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_escalate_to_agent")
        # Integrate with chat platform's handoff API here if needed
        return []
