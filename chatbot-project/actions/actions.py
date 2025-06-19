"""Custom actions for the Customer Care chatbot."""

import random
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionTellJoke(Action):
    """Send a random joke to the user."""

    def name(self) -> Text:
        return "action_tell_joke"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer I needed a break, and it said 'No problem — I'll go to sleep.'",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
        ]
        joke = random.choice(jokes)
        dispatcher.utter_message(text=joke)
        return []
