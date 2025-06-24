from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import pytz

class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now(pytz.utc).strftime("%H:%M")
        dispatcher.utter_message(text=f"The current time is {current_time} UTC.")
        return []

class ActionGetDate(Action):
    def name(self) -> Text:
        return "action_get_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_date = datetime.now(pytz.utc).strftime("%A, %B %d, %Y")
        dispatcher.utter_message(text=f"Today's date is {current_date}.")
        return []

class ActionTellDateTime(Action):
    def name(self) -> Text:
        return "action_tell_datetime"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_datetime = datetime.now(pytz.utc).strftime("%A, %B %d, %Y at %H:%M %Z")
        dispatcher.utter_message(text=f"The current date and time is {current_datetime}.")
        return []

class ActionIncrementFallbackCount(Action):
    def name(self) -> Text:
        return "action_increment_fallback_count"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # This is a placeholder action. You can add logic here if needed.
        return []
