from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text
import random

class ActionTellJoke(Action):
    """Send a random joke to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_joke"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer I needed a break, and it said 'No problem — I'll go to sleep.'",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "I asked the IT guy, 'Why is my computer so slow?' He said, 'You have too many tabs open.' If only that worked for my life too.",
            "Why don't programmers like nature? It has too many bugs.",
            "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
            "I'm reading a book about anti-gravity. It's impossible to put down!",
        ]
        joke = random.choice(jokes)
        dispatcher.utter_message(text=joke, intent="tell_joke", confidence=1.0)
        return []
