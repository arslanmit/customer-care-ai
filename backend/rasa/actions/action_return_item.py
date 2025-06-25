from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionReturnItem(Action):
    def name(self) -> Text:
        return "action_return_item"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Give the user instructions to start a return."""

        dispatcher.utter_message(
            text="To return an item, please visit your orders page and click 'Start a return'."
        )
        return []
