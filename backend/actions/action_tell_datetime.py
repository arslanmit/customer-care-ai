from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text
from datetime import datetime

class ActionTellDateTime(Action):
    """Provide the current date and time to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_datetime"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"The current date and time is {now}."
        dispatcher.utter_message(text=message)
        return []
