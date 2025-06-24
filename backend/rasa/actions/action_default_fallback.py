from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text
import logging

logger = logging.getLogger(__name__)

class ActionDefaultFallback(Action):
    """
    Executes the fallback action and goes back to the previous state of the dialogue.
    """
    def name(self) -> Text:
        return "action_default_fallback"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.debug("Triggered default fallback action.")
        latest_message = tracker.latest_message
        if latest_message is None:
            logger.warning("No latest message found in tracker.")
            return []
        intent = latest_message.get("intent", {}).get("name")
        entities = latest_message.get("entities", [])
        logger.debug(f"Fallback triggered with intent: {intent}, entities: {entities}")
        if intent == "out_of_scope":
            dispatcher.utter_message(response="utter_out_of_scope")
            return []
        dispatcher.utter_message(response="utter_default")
        return [UserUtteranceReverted()]
