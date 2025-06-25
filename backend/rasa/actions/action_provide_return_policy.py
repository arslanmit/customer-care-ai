from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionProvideReturnPolicy(Action):
    def name(self) -> Text:
        return "action_provide_return_policy"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Inform the user about the return policy."""

        message = (
            "Our standard return policy allows returns within 30 days of delivery. "
            "Items must be in original condition."
        )
        dispatcher.utter_message(text=message)
        return []
