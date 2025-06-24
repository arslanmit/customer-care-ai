from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionCheckOrderStatus(Action):
    def name(self) -> Text:
        return "action_check_order_status"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_provide_order_status.")
        return []
