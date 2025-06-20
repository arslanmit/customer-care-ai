from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime

class ActionTellTime(Action):
    def name(self) -> str:
        return "action_tell_time"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        now = datetime.now().strftime("%H:%M")
        dispatcher.utter_message(text=f"The current time is {now}.")
        return []
