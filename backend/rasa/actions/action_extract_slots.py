from typing import Dict, Text, Any, List, Optional

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionExtractOrderNumber(Action):
    def name(self) -> Text:
        return "action_extract_order_number"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        order_number = next(tracker.get_latest_entity_values("order_number"), None)
        if order_number:
            return [SlotSet("order_number", order_number)]
        return []

class ActionExtractProductId(Action):
    def name(self) -> Text:
        return "action_extract_product_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        product_id = next(tracker.get_latest_entity_values("product_id"), None)
        if product_id:
            return [SlotSet("product_id", product_id)]
        return []

class ActionExtractEmail(Action):
    def name(self) -> Text:
        return "action_extract_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        email = next(tracker.get_latest_entity_values("email"), None)
        if email:
            return [SlotSet("email", email)]
        return []

class ActionExtractPhoneNumber(Action):
    def name(self) -> Text:
        return "action_extract_phone_number"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = next(tracker.get_latest_entity_values("phone_number"), None)
        if phone_number:
            return [SlotSet("phone_number", phone_number)]
        return []

class ActionExtractDate(Action):
    def name(self) -> Text:
        return "action_extract_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        date = next(tracker.get_latest_entity_values("date"), None)
        if date:
            return [SlotSet("requested_date", date)]
        return []

class ActionExtractTime(Action):
    def name(self) -> Text:
        return "action_extract_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        time = next(tracker.get_latest_entity_values("time"), None)
        if time:
            return [SlotSet("requested_time", time)]
        return []

class ActionExtractLanguage(Action):
    def name(self) -> Text:
        return "action_extract_language"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        language = next(tracker.get_latest_entity_values("language"), None)
        if language:
            return [SlotSet("language", language)]
        return []

class ActionExtractFirstName(Action):
    def name(self) -> Text:
        return "action_extract_first_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        first_name = next(tracker.get_latest_entity_values("first_name"), None)
        if first_name:
            return [SlotSet("first_name", first_name)]
        return []

class ActionExtractLastName(Action):
    def name(self) -> Text:
        return "action_extract_last_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        last_name = next(tracker.get_latest_entity_values("last_name"), None)
        if last_name:
            return [SlotSet("last_name", last_name)]
        return []

class ActionExtractComplaintType(Action):
    def name(self) -> Text:
        return "action_extract_complaint_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        complaint_type = next(tracker.get_latest_entity_values("complaint_type"), None)
        if complaint_type:
            return [SlotSet("complaint_type", complaint_type)]
        return []

class ActionExtractComplaintDetails(Action):
    def name(self) -> Text:
        return "action_extract_complaint_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        complaint_details = next(tracker.get_latest_entity_values("complaint_details"), None)
        if complaint_details:
            return [SlotSet("complaint_details", complaint_details)]
        return []

class ActionExtractCustomerEmail(Action):
    def name(self) -> Text:
        return "action_extract_customer_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        email = next(tracker.get_latest_entity_values("email"), None)
        if email:
            return [SlotSet("customer_email", email)]
        return []
