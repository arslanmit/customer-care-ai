from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Dict, List, Text

class ActionCheckOrderStatus(Action):
    def name(self) -> Text:
        return "action_check_order_status"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Return a fake order status if an order number is provided."""

        order_number = tracker.get_slot("order_number")
        if not order_number:
            dispatcher.utter_message(response="utter_ask_order_number")
            return []

        # Dummy order database
        fake_db = {
            "1001": "shipped",
            "1002": "processing",
            "1003": "delivered",
        }

        status = fake_db.get(str(order_number), "not found")
        if status == "not found":
            dispatcher.utter_message(
                text=f"I couldn't find an order with number {order_number}."
            )
        else:
            dispatcher.utter_message(
                text=f"Your order {order_number} is currently {status}."
            )

        return []
