from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text
from datetime import datetime

class ActionTellDate(Action):
    """Provide the current date to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        today = datetime.now().strftime("%Y-%m-%d")
        message = f"Today's date is {today}."
        dispatcher.utter_message(text=message)
        return []
