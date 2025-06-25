from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionContactSupport(Action):
    def name(self) -> Text:
        return "action_contact_support"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Provide contact information for human support."""

        dispatcher.utter_message(
            text="You can reach our support team at support@example.com or call 1-800-EXAMPLE."
        )
        return []
