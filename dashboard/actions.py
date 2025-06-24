import random
from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionTellTime(Action):
    """Action to tell the current time."""

    def name(self) -> Text:
        return "action_tell_time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        now = datetime.now().strftime("%H:%M")
        response = f"The current time is {now}."
        dispatcher.utter_message(text=response)
        log_event(
            {
                "session_id": tracker.sender_id,
                "sender": "bot",
                "message_text": response,
                "intent": "tell_time",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return []


class ActionTellDate(Action):
    """Action to tell the current date."""

    def name(self) -> Text:
        return "action_tell_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        today = datetime.now().strftime("%Y-%m-%d")
        response = f"Today's date is {today}."
        dispatcher.utter_message(text=response)
        log_event(
            {
                "session_id": tracker.sender_id,
                "sender": "bot",
                "message_text": response,
                "intent": "tell_date",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return []


class ActionTellDateTime(Action):
    """Action to tell the current date and time."""

    def name(self) -> Text:
        return "action_tell_datetime"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        response = f"The current date and time is {now}."
        dispatcher.utter_message(text=response)
        log_event(
            {
                "session_id": tracker.sender_id,
                "sender": "bot",
                "message_text": response,
                "intent": "tell_datetime",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return []


class ActionTellJoke(Action):
    """Action to tell a joke."""

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
            (
                "Did you hear about the mathematician who's afraid of negative numbers? "
                "He'll stop at nothing to avoid them!"  # noqa: E501
            ),
            "Why don't skeletons fight each other? They don't have the guts!",  # noqa: E501
            "I'm reading a book about anti-gravity. It's impossible to put down!",
        ]
        joke = random.choice(jokes)
        dispatcher.utter_message(text=joke)
        log_event(
            {
                "session_id": tracker.sender_id,
                "sender": "bot",
                "message_text": joke,
                "intent": "tell_joke",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return []


class ActionSetLanguage(Action):
    """Action to set the user's preferred language."""

    def name(self) -> Text:
        return "action_set_language"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        language = next(tracker.get_latest_entity_values("language"), None)
        if language:
            return [SlotSet("language", language.lower())]
        return []


class ActionHandoffToHuman(Action):
    """Action to handle transfer to a human agent."""

    def name(self) -> Text:
        return "action_handoff_to_human"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_escalate_to_agent")
        # Here you would typically integrate with your chat platform's handoff API
        return []


class ActionIncrementFallbackCount(Action):
    """Action to increment the fallback counter."""

    def name(self) -> Text:
        return "action_increment_fallback_count"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        current_fallbacks = tracker.get_slot("num_fallbacks") or 0
        return [SlotSet("num_fallbacks", current_fallbacks + 1)]


class ActionAskOrderNumber(Action):
    """Action to ask for order number."""

    def name(self) -> Text:
        return "action_ask_order_number"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_ask_order_number")
        return []


class ValidateNameForm(FormValidationAction):
    """Validates the name form."""

    def name(self) -> Text:
        return "validate_name_form"

    def validate_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate name value."""
        if not slot_value or len(slot_value.strip()) < 2:
            dispatcher.utter_message(
                text=("Please provide a valid name (at least 2 characters).")
            )
            return {"name": None}
        return {"name": slot_value}
