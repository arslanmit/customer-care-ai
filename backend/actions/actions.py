"""Custom actions for the Customer Care chatbot."""

import logging
import random
from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from sanic import response
from sanic.blueprints import Blueprint

logger = logging.getLogger(__name__)

# Language detection removed - English only


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

        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer I needed a break, "
            "and it said 'No problem — I'll go to sleep.'",
            (
                "Why did the scarecrow win an award? "
                "Because he was outstanding in his field!"
            ),
            "I asked the IT guy, 'Why is my computer so slow?' "
            "He said, 'You have too many tabs open.' "
            "If only that worked for my life too.",
            "Why don't programmers like nature? It has too many bugs.",
            (
                "Did you hear about the mathematician who's afraid of negative "
                "numbers? He'll stop at nothing to avoid them!"
            ),
            ("I'm reading a book about anti-gravity. " "It's impossible to put down!"),
        ]

        available_jokes = jokes
        joke = random.choice(available_jokes)

        # Add intent metadata for analytics
        dispatcher.utter_message(
            text=joke,
            intent="tell_joke",
            confidence=1.0,
        )
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
        now = datetime.now()

        time_formats = {
            "en": "%I:%M %p",  # 12-hour format with AM/PM
            "es": "%H:%M",  # 24-hour format
            "fr": "%H h %M",  # French format
            "de": "%H:%M",  # 24-hour format
            "tr": "%H:%M",  # 24-hour format
        }

        try:
            time_messages = {
                "en": (
                    f"The current time is "
                    f"{now.strftime(time_formats.get('en', '%H:%M'))}"
                ),
                "es": (
                    f"La hora actual es "
                    f"{now.strftime(time_formats.get('es', '%H:%M'))}"
                ),
                "fr": (
                    f"L'heure actuelle est "
                    f"{now.strftime(time_formats.get('fr', '%H:%M'))}"
                ),
                "de": (
                    f"Die aktuelle Zeit ist "
                    f"{now.strftime(time_formats.get('de', '%H:%M'))} Uhr"
                ),
                "tr": (
                    f"Şu anki saat " f"{now.strftime(time_formats.get('tr', '%H:%M'))}"
                ),
            }
        except Exception as e:
            logger.error(f"Error formatting time: {e}")
            # Fallback to a simple format that should work everywhere
            time_messages = {
                "en": (f"The current time is " f"{now.strftime('%H:%M')}"),
                "es": (f"La hora actual es " f"{now.strftime('%H:%M')}"),
                "fr": (f"L'heure actuelle est " f"{now.strftime('%H:%M')}"),
                "de": (f"Die aktuelle Zeit ist " f"{now.strftime('%H:%M')}"),
                "tr": (f"Şu anki saat " f"{now.strftime('%H:%M')}"),
            }

        # Get the message in the user's language, fallback to English
        message = time_messages["en"]

        # Add intent metadata for analytics
        dispatcher.utter_message(
            text=message,
            intent="ask_time",
            confidence=1.0,
        )
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
        now = datetime.now()

        # Format date based on language
        date_formats = {
            "en": "%A, %B %d, %Y",  # Tuesday, June 20, 2023
            "es": "%A, %d de %B de %Y",  # martes, 20 de junio de 2023
            "fr": "%A %d %B %Y",  # mardi 20 juin 2023
            "de": "%A, %d. %B %Y",  # Dienstag, 20. Juni 2023
            "tr": "%d %B %Y %A",  # 20 Haziran 2023 Salı
        }

        try:
            date_messages = {
                "en": (f"Today is " f"{now.strftime(date_formats['en'])}"),
                "es": (f"Hoy es " f"{now.strftime(date_formats['es'])}"),
                "fr": (f"Nous sommes le " f"{now.strftime(date_formats['fr'])}"),
                "de": (f"Heute ist " f"{now.strftime(date_formats['de'])}"),
                "tr": (f"Bugün " f"{now.strftime(date_formats['tr'])}"),
            }
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            # Fallback to a simple format
            date_messages = {
                "en": (f"Today is " f"{now.strftime('%Y-%m-%d')}"),
                "es": (f"Hoy es " f"{now.strftime('%Y-%m-%d')}"),
                "fr": (f"Aujourd'hui c'est le " f"{now.strftime('%Y-%m-%d')}"),
                "de": (f"Heute ist der " f"{now.strftime('%d.%m.%Y')}"),
                "tr": (f"Bugünün tarihi " f"{now.strftime('%d.%m.%Y')}"),
            }

        # Get the message in the user's language, fallback to English
        message = date_messages["en"]

        # Add intent metadata for analytics
        dispatcher.utter_message(
            text=message,
            intent="ask_date",
            confidence=1.0,
        )
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
        now = datetime.now()

        # Format date and time based on language
        datetime_formats = {
            "en": {
                "date": "%A, %B %d, %Y",
                "time": "%I:%M %p",
                "message": "Today is {date} and the current time is {time}",
            },
            "es": {
                "date": "%A, %d de %B de %Y",
                "time": "%H:%M",
                "message": "Hoy es {date} y la hora actual es {time}",
            },
            "fr": {
                "date": "%A %d %B %Y",
                "time": "%H h %M",
                "message": "Nous sommes le {date} et il est {time}",
            },
            "de": {
                "date": "%A, %d. %B %Y",
                "time": "%H:%M",
                "message": "Heute ist {date} und es ist {time} Uhr",
            },
            "tr": {
                "date": "%d %B %Y %A",
                "time": "%H:%M",
                "message": "Bugün {date} ve saat şu an {time}",
            },
        }

        try:
            fmt = datetime_formats.get("en")
            date_str = now.strftime(fmt["date"])
            time_str = now.strftime(fmt["time"])
            message = fmt["message"].format(date=date_str, time=time_str)
        except Exception as e:
            logger.error(f"Error formatting datetime: {e}")
            # Fallback to simple format
            fallback_date = now.strftime("%Y-%m-%d")
            fallback_time = now.strftime("%H:%M")
            message = (
                f"Today is {fallback_date} and the current time is {fallback_time}"
            )

        # Add intent metadata for analytics
        dispatcher.utter_message(
            text=message,
            intent="ask_datetime",
            confidence=1.0,
        )
        return []


# ActionSetLanguage class removed - English only now


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
        resp = (
            supabase.table("fallbacks")
            .select("count")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        fallback_count = (
            (resp.data.get("count") if resp.data else 0)
            if resp.status_code == 200
            else 0
        )
        # Update local tracker slot fallback count
        fallback_count += 1
        # Upsert the new count back to Supabase
        supabase.table("fallbacks").upsert(
            {"user_id": user_id, "count": fallback_count}
        ).execute()

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
        logger.info(
            "Handing off conversation to human agent. User message: %s",
            tracker.latest_message.get("text"),
        )

        # Reset fallback counter after handoff
        return [SlotSet("num_fallbacks", 0), SlotSet("escalated", True)]


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

        # For now, we'll use the default English response from domain.yml
        # In a real implementation, you might want to add multilingual support here
        dispatcher.utter_message(response="utter_ask_order_number")

        return []


class ActionDefaultFallback(Action):
    """
    Executes the fallback action and goes back to the previous state of the dialogue.
    """

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """
        Default fallback which attempts to recover from user messages
        which don't fit the conversation flow.

        This action will log the fallback and send a default response.
        """
        # Log the fallback
        logger.debug("Triggered default fallback action.")

        # Get the language

        # Get the latest user message
        latest_message = tracker.latest_message
        if latest_message is None:
            logger.warning("No latest message found in tracker.")
            return []

        # Log the intent and entities for debugging
        intent = latest_message.get("intent", {}).get("name")
        entities = latest_message.get("entities", [])
        logger.debug(f"Fallback triggered with intent: {intent}, entities: {entities}")

        # Check if this is an out of scope message
        if intent == "out_of_scope":
            dispatcher.utter_message(response="utter_out_of_scope")
            return []

        # Default fallback response (English only)
        dispatcher.utter_message(response="utter_default")

        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]


# === Placeholder implementations for missing actions ===
class ActionCheckOrderStatus(Action):
    def name(self) -> Text:
        return "action_check_order_status"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text=("[Placeholder] This is action_provide_" "order_status.")
        )
        return []


class ActionAskHowCanIHelp(Action):
    def name(self) -> Text:
        return "action_ask_how_can_i_help"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text=("[Placeholder] This is action_ask_how_" "can_i_help.")
        )
        return []


class ActionReturnItem(Action):
    def name(self) -> Text:
        return "action_return_item"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text=("[Placeholder] This is action_return_" "item."))
        return []


class ActionContactSupport(Action):
    def name(self) -> Text:
        return "action_contact_support"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text=("[Placeholder] This is action_contact_" "support.")
        )
        return []


class ActionProvideReturnPolicy(Action):
    def name(self) -> Text:
        return "action_provide_return_policy"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text=("[Placeholder] This is action_provide_" "return_policy.")
        )
        return []


class ActionProvideOrderStatus(Action):
    def name(self) -> Text:
        return "action_provide_order_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text=(
                "I'll check your order status. "
                "Could you please provide your order "
                "number?"
            )
        )
        return []


# Favicon handler to suppress 404 errors
favicon_bp = Blueprint("favicon")


@favicon_bp.get("/favicon.ico")
async def favicon(request):
    # Return a 204 No Content response with empty body
    return response.raw(b"", status=204, headers={"Content-Type": "image/x-icon"})
