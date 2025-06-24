from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionProvideReturnPolicy(Action):
    def name(self) -> Text:
        return "action_provide_return_policy"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_provide_return_policy.")
        return []
