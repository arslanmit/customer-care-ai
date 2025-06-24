from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionAskHowCanIHelp(Action):
    def name(self) -> Text:
        return "action_ask_how_can_i_help"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_ask_how_can_i_help.")
        return []
