from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionAskHowCanIHelp(Action):
    def name(self) -> Text:
        return "action_ask_how_can_i_help"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Politely ask the user how the assistant can help."""

        dispatcher.utter_message(text="How can I help you today?")
        return []
