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
    """Get the current language from tracker or default to English.
    
    Args:
        tracker: The conversation tracker
        
    Returns:
        The detected language code (en, es, fr, de, tr)
    """
    try:
        # Check request language from header if available
        language_header = next(
            (e for e in tracker.events if e.get('event') == 'user' and e.get('metadata', {}).get('language')),
            None
        )
        
        if language_header:
            lang_code = language_header.get('metadata', {}).get('language', 'en')
            if lang_code in ['en', 'es', 'fr', 'de', 'tr']:
                return lang_code
        
        # Get language from slot if set
        language = tracker.get_slot('language')
        if language and language in ['en', 'es', 'fr', 'de', 'tr']:
            return language
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        
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
            ],
            'tr': [
                "Bilim insanları neden atomlara güvenmez? Çünkü her şeyi onlar uydurur!",
                "Bilgisayarıma ara vermem gerektiğini söyledim, o da 'Sorun değil — ben uyuyacağım.' dedi.",
                "Korkuluk neden ödül kazandı? Çünkü alanında üstündü!",
                "Programcılar neden doğayı sevmez? Çünkü içinde çok fazla hata vardır."
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
            'de': "%H:%M",    # 24-hour format
            'tr': "%H:%M"     # 24-hour format
        }
        
        try:
            time_messages = {
                'en': f"The current time is {now.strftime(time_formats.get('en', '%H:%M'))}",
                'es': f"La hora actual es {now.strftime(time_formats.get('es', '%H:%M'))}",
                'fr': f"L'heure actuelle est {now.strftime(time_formats.get('fr', '%H:%M'))}",
                'de': f"Die aktuelle Zeit ist {now.strftime(time_formats.get('de', '%H:%M'))} Uhr",
                'tr': f"Şu anki saat {now.strftime(time_formats.get('tr', '%H:%M'))}"
            }
        except Exception as e:
            logger.error(f"Error formatting time: {e}")
            # Fallback to a simple format that should work everywhere
            time_messages = {
                'en': f"The current time is {now.strftime('%H:%M')}",
                'es': f"La hora actual es {now.strftime('%H:%M')}",
                'fr': f"L'heure actuelle est {now.strftime('%H:%M')}",
                'de': f"Die aktuelle Zeit ist {now.strftime('%H:%M')}",
                'tr': f"Şu anki saat {now.strftime('%H:%M')}"
            }
        
        # Get the message in the user's language, fallback to English
        message = time_messages.get(language, time_messages['en'])
        
        # Add intent metadata for analytics
        dispatcher.utter_message(text=message, intent="ask_time", confidence=1.0)
        
        return []


class ActionTellDate(Action):
    """Provide the current date to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        language = get_language(tracker)
        now = datetime.now()
        
        # Format date based on language
        date_formats = {
            'en': "%A, %B %d, %Y",  # Tuesday, June 20, 2023
            'es': "%A, %d de %B de %Y",  # martes, 20 de junio de 2023
            'fr': "%A %d %B %Y",  # mardi 20 juin 2023
            'de': "%A, %d. %B %Y",  # Dienstag, 20. Juni 2023
            'tr': "%d %B %Y %A"  # 20 Haziran 2023 Salı
        }
        
        try:
            date_messages = {
                'en': f"Today is {now.strftime(date_formats['en'])}",
                'es': f"Hoy es {now.strftime(date_formats['es'])}",
                'fr': f"Nous sommes le {now.strftime(date_formats['fr'])}",
                'de': f"Heute ist {now.strftime(date_formats['de'])}",
                'tr': f"Bugün {now.strftime(date_formats['tr'])}"
            }
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            # Fallback to a simple format
            date_messages = {
                'en': f"Today is {now.strftime('%Y-%m-%d')}",
                'es': f"Hoy es {now.strftime('%Y-%m-%d')}",
                'fr': f"Aujourd'hui c'est le {now.strftime('%Y-%m-%d')}",
                'de': f"Heute ist der {now.strftime('%d.%m.%Y')}",
                'tr': f"Bugünün tarihi {now.strftime('%d.%m.%Y')}"
            }
        
        # Get the message in the user's language, fallback to English
        message = date_messages.get(language, date_messages['en'])
        
        # Add intent metadata for analytics
        dispatcher.utter_message(text=message, intent="ask_date", confidence=1.0)
        
        return []


class ActionTellDateTime(Action):
    """Provide the current date and time to the user in their preferred language."""

    def name(self) -> Text:
        return "action_tell_datetime"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        language = get_language(tracker)
        now = datetime.now()
        
        # Format date and time based on language
        datetime_formats = {
            'en': {
                'date': "%A, %B %d, %Y",
                'time': "%I:%M %p",
                'message': "Today is {date} and the current time is {time}"
            },
            'es': {
                'date': "%A, %d de %B de %Y",
                'time': "%H:%M",
                'message': "Hoy es {date} y la hora actual es {time}"
            },
            'fr': {
                'date': "%A %d %B %Y",
                'time': "%H h %M",
                'message': "Nous sommes le {date} et il est {time}"
            },
            'de': {
                'date': "%A, %d. %B %Y",
                'time': "%H:%M",
                'message': "Heute ist {date} und es ist {time} Uhr"
            },
            'tr': {
                'date': "%d %B %Y %A",
                'time': "%H:%M",
                'message': "Bugün {date} ve saat şu an {time}"
            }
        }
        
        try:
            fmt = datetime_formats.get(language, datetime_formats['en'])
            date_str = now.strftime(fmt['date'])
            time_str = now.strftime(fmt['time'])
            message = fmt['message'].format(date=date_str, time=time_str)
        except Exception as e:
            logger.error(f"Error formatting datetime: {e}")
            # Fallback to simple format
            fallback_date = now.strftime('%Y-%m-%d')
            fallback_time = now.strftime('%H:%M')
            message = f"Today is {fallback_date} and the current time is {fallback_time}"
        
        # Add intent metadata for analytics
        dispatcher.utter_message(text=message, intent="ask_datetime", confidence=1.0)
        
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
        # Extract language from message, default to English
        message = tracker.latest_message.get('text', '').lower()
        
        language = 'en'  # Default
        
        try:
            # Language detection based on keywords
            language_keywords = {
                'es': ['spanish', 'español', 'espanol', 'castellano'],
                'fr': ['french', 'français', 'francais', 'le français'],
                'de': ['german', 'deutsch', 'deutsche', 'germanisch'],
                'tr': ['turkish', 'türkçe', 'turkce', 'türk'],
                'en': ['english', 'inglés', 'ingles']
            }
            
            # Check each language's keywords
            for lang_code, keywords in language_keywords.items():
                if any(keyword in message for keyword in keywords):
                    language = lang_code
                    break
                    
            # Additional check for possible language codes directly in the message
            lang_codes = ['en', 'es', 'fr', 'de', 'tr']
            for code in lang_codes:
                # Check if the code appears as a standalone word
                if f" {code} " in f" {message} " or message == code:
                    language = code
                    break
            
            logger.info(f"Setting language to {language} based on message: {message}")
            
        except Exception as e:
            logger.error(f"Error detecting language from message '{message}': {e}")
        
        # The response will come from domain.yml utter_language_changed
        # with the appropriate language variant
        
        return [SlotSet("language", language)]
