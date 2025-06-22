"""
This module contains custom actions for the Rasa chatbot.
"""
from typing import Any, Text, Dict, List
from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionTellTime(Action):
    """An example action that tells the current time."""
    
    def name(self) -> Text:
        """Return the unique identifier of the action."""
        return "action_tell_time"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """
        Execute the action to tell the current time.
        
        Args:
            dispatcher: The dispatcher to send messages back to the user
            tracker: The current conversation tracker
            domain: The bot's domain
            
        Returns:
            List of events to be processed by Rasa
        """
        current_time = datetime.now().strftime("%H:%M")
        dispatcher.utter_message(text=f"The current time is {current_time}.")
        return []
