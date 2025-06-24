from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ActionTellTime(Action):
    """Provide the current time to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        now = datetime.now()
        time_formats = {
            "en": "%I:%M %p",
            "es": "%H:%M",
            "fr": "%H h %M",
            "de": "%H:%M",
            "tr": "%H:%M",
        }
        try:
            time_messages = {
                "en": f"The current time is {now.strftime(time_formats.get('en', '%H:%M'))}",
                "es": f"La hora actual es {now.strftime(time_formats.get('es', '%H:%M'))}",
                "fr": f"L'heure actuelle est {now.strftime(time_formats.get('fr', '%H:%M'))}",
                "de": f"Die aktuelle Zeit ist {now.strftime(time_formats.get('de', '%H:%M'))} Uhr",
                "tr": f"Şu anki saat {now.strftime(time_formats.get('tr', '%H:%M'))}",
            }
        except Exception as e:
            logger.error(f"Error formatting time: {e}")
            time_messages = {lang: f"The current time is {now.strftime('%H:%M')}" for lang in time_formats}
        message = time_messages["en"]
        dispatcher.utter_message(text=message)
        return []
