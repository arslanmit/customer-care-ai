"""Custom actions for the Customer Care chatbot."""

import random
import logging
from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

logger = logging.getLogger(__name__)


def get_language(tracker: Tracker) -> Text:
    """Get the current language from tracker or default to English."""
    # Check request language from header if available
    language_header = next(
        (e for e in tracker.events if e.get('event') == 'user' and e.get('metadata', {}).get('language')),
        None
    )
    
    if language_header:
        return language_header.get('metadata', {}).get('language', 'en')
    
    # Get language from slot if set
    language = tracker.get_slot('language')
    if language:
        return language
        
    return 'en'  # Default to English


class ActionTellJoke(Action):
    """Send a random joke to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_joke"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        language = get_language(tracker)
        
        jokes = {
            'en': [
                "Why don't scientists trust atoms? Because they make up everything!",
                "I told my computer I needed a break, and it said 'No problem — I'll go to sleep.'",
                "Why did the scarecrow win an award? Because he was outstanding in his field!",
                "I asked the IT guy, 'Why is my computer so slow?' He said, 'You have too many tabs open.' If only that worked for my life too.",
                "Why don't programmers like nature? It has too many bugs."
            ],
            'es': [
                "¿Por qué los científicos no confían en los átomos? ¡Porque lo componen todo!",
                "Le dije a mi computadora que necesitaba un descanso y me dijo 'No hay problema, me voy a dormir'.",
                "¿Por qué el espantapájaros ganó un premio? ¡Porque era sobresaliente en su campo!",
                "¿Qué le dice un bit al otro? Nos vemos en el bus."
            ],
            'fr': [
                "Pourquoi les scientifiques ne font pas confiance aux atomes ? Parce qu'ils inventent tout !",
                "J'ai dit à mon ordinateur que j'avais besoin d'une pause, et il a dit 'Pas de problème — je vais dormir.'",
                "Pourquoi l'épouvantail a-t-il gagné un prix ? Parce qu'il était excellent dans son domaine !"
            ],
            'de': [
                "Warum vertrauen Wissenschaftler Atomen nicht? Weil sie alles erfinden!",
                "Ich habe meinem Computer gesagt, dass ich eine Pause brauche, und er sagte 'Kein Problem — ich schlafe ein.'",
                "Warum hat die Vogelscheuche einen Preis gewonnen? Weil sie auf ihrem Gebiet hervorragend war!"
            ]
        }
        
        # Fall back to English if the language is not supported
        available_jokes = jokes.get(language, jokes['en'])
        joke = random.choice(available_jokes)
        
        # Add intent metadata for analytics
        dispatcher.utter_message(text=joke, intent="tell_joke", confidence=1.0)
        
        return []


class ActionTellTime(Action):
    """Provide the current time to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        language = get_language(tracker)
        now = datetime.now()
        
        time_formats = {
            'en': "%I:%M %p",  # 12-hour format with AM/PM
            'es': "%H:%M",    # 24-hour format
            'fr': "%H h %M",  # French format
            'de': "%H:%M"     # 24-hour format
        }
        
        time_messages = {
            'en': f"The current time is {now.strftime(time_formats.get('en', '%H:%M'))}",
            'es': f"La hora actual es {now.strftime(time_formats.get('es', '%H:%M'))}",
            'fr': f"L'heure actuelle est {now.strftime(time_formats.get('fr', '%H:%M'))}",
            'de': f"Die aktuelle Zeit ist {now.strftime(time_formats.get('de', '%H:%M'))} Uhr"
        }
        
        # Get the message in the user's language, fallback to English
        message = time_messages.get(language, time_messages['en'])
        
        # Add intent metadata for analytics
        dispatcher.utter_message(text=message, intent="ask_time", confidence=1.0)
        
        return []


class ActionSetLanguage(Action):
    """Set the user's preferred language."""

    def name(self) -> Text:
        return "action_set_language"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Extract language entity from message, default to English
        message = tracker.latest_message.get('text', '').lower()
        
        language = 'en'  # Default
        
        # Simple language detection based on intent
        if 'spanish' in message or 'español' in message or 'espanol' in message:
            language = 'es'
        elif 'french' in message or 'français' in message or 'francais' in message:
            language = 'fr'
        elif 'german' in message or 'deutsch' in message:
            language = 'de'
        elif 'english' in message or 'inglés' in message or 'ingles' in message:
            language = 'en'
            
        logger.debug(f"Setting language to {language}")
        
        # The response will come from domain.yml utter_language_changed
        # with the appropriate language variant
        
        return [SlotSet("language", language)]
