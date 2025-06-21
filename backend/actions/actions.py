"""Custom actions for the Customer Care chatbot."""

import random
import logging
from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted

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
        language = next(tracker.get_latest_entity_values("language"), None)
        
        if not language:
            # If no language entity was found, try to extract from the latest message
            language = tracker.latest_message.get('text', '').lower()
            
            # Simple language detection from text
            if 'spanish' in language or 'español' in language or 'espanol' in language:
                language = 'es'
            elif 'french' in language or 'français' in language or 'francais' in language:
                language = 'fr'
            elif 'german' in language or 'deutsch' in language:
                language = 'de'
            elif 'turkish' in language or 'türkçe' in language or 'turkce' in language:
                language = 'tr'
            else:
                language = 'en'  # Default to English
        
        # Ensure language is in our supported languages
        if language not in ['en', 'es', 'fr', 'de', 'tr']:
            language = 'en'
        
        return [SlotSet("language", language)]


class ActionIncrementFallbackCount(Action):
    """Increment the fallback counter and handle escalation if needed."""

    def name(self) -> Text:
        return "action_increment_fallback_count"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Persist fallback count to Supabase
        from backend.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        user_id = tracker.sender_id
        # Fetch current fallback count from Supabase, default to 0 if not found
        resp = supabase.table("fallbacks").select("count").eq("user_id", user_id).single().execute()
        fallback_count = (resp.data.get("count") if resp.data else 0) if resp.status_code == 200 else 0
        # Update local tracker slot fallback count
        fallback_count += 1
        # Upsert the new count back to Supabase
        supabase.table("fallbacks").upsert({"user_id": user_id, "count": fallback_count}).execute()
        
        # Reset fallback count if we had a successful interaction
        last_intent = tracker.latest_message.get("intent", {}).get("name")
        if last_intent != "nlu_fallback":
            fallback_count = 0
        
        return [SlotSet("num_fallbacks", fallback_count)]


class ActionHandoffToHuman(Action):
    """Handle the handoff to a human agent."""

    def name(self) -> Text:
        return "action_handoff_to_human"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # In a real implementation, you would:
        # 1. Log the handoff
        # 2. Create a support ticket
        # 3. Notify the support team
        # 4. Update the conversation state
        
        # For now, we'll just log it and send a message
        logger.info(f"Handing off conversation to human agent. User message: {tracker.latest_message.get('text')}")
        
        # Reset fallback counter after handoff
        return [
            SlotSet("num_fallbacks", 0),
            SlotSet("escalated", True)
        ]


class ActionAskOrderNumber(Action):
    """Ask the user for their order number to check the status."""

    def name(self) -> Text:
        return "action_ask_order_number"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """
        Ask the user for their order number to check the status.
        """
        # Get the language
        language = get_language(tracker)
        
        # For now, we'll use the default English response from domain.yml
        # In a real implementation, you might want to add multilingual support here
        dispatcher.utter_message(response="utter_ask_order_number")
        
        return []


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """
        Default fallback which attempts to recover from user messages which don't fit the conversation flow.
        """
        # Log the fallback
        logger.debug("Triggered default fallback action.")
        
        # Get the language
        language = get_language(tracker)
        
        # Get the latest user message
        latest_message = tracker.latest_message
        if latest_message is None:
            logger.warning("No latest message found in tracker.")
            return []
            
        # Log the intent and entities for debugging
        intent = latest_message.get('intent', {}).get('name')
        entities = latest_message.get('entities', [])
        logger.debug(f"Fallback triggered with intent: {intent}, entities: {entities}")
        
        # Check if this is an out of scope message
        if intent == 'out_of_scope':
            if language == 'es':
                dispatcher.utter_message(response="utter_out_of_scope_es")
            elif language == 'fr':
                dispatcher.utter_message(response="utter_out_of_scope_fr")
            elif language == 'de':
                dispatcher.utter_message(response="utter_out_of_scope_de")
            elif language == 'tr':
                dispatcher.utter_message(response="utter_out_of_scope_tr")
            else:
                dispatcher.utter_message(response="utter_out_of_scope")
            return []
            
        # For other fallbacks, try to respond based on language
        if language == 'es':
            dispatcher.utter_message(text="Lo siento, no estoy seguro de lo que quieres decir. ¿Podrías reformularlo?")
        elif language == 'fr':
            dispatcher.utter_message(text="Je suis désolé, je ne suis pas sûr de comprendre. Pourriez-vous reformuler ?")
        elif language == 'de':
            dispatcher.utter_message(text="Es tut mir leid, ich bin mir nicht sicher, was Sie meinen. Könnten Sie es anders formulieren?")
        elif language == 'tr':
            dispatcher.utter_message(text="Üzgünüm, ne demek istediğinizden emin değilim. Başka şekilde ifade edebilir misiniz?")
        else:
            dispatcher.utter_message(response="utter_default")
            
        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]


# === Placeholder implementations for missing actions ===
class ActionCheckOrderStatus(Action):
    def name(self) -> Text:
        return "action_check_order_status"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_check_order_status.")
        return []

class ActionAskHowCanIHelp(Action):
    def name(self) -> Text:
        return "action_ask_how_can_i_help"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_ask_how_can_i_help.")
        return []

class ActionReturnItem(Action):
    def name(self) -> Text:
        return "action_return_item"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_return_item.")
        return []

class ActionContactSupport(Action):
    def name(self) -> Text:
        return "action_contact_support"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_contact_support.")
        return []

class ActionProvideReturnPolicy(Action):
    def name(self) -> Text:
        return "action_provide_return_policy"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_provide_return_policy.")
        return []

class ActionProvideOrderStatus(Action):
    def name(self) -> Text:
        return "action_provide_order_status"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_provide_order_status.")
        return []
