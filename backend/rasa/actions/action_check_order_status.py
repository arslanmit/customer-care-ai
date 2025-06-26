from rasa_sdk import Action
from typing import Text

class ActionCheckOrderStatus(Action):
    def name(self) -> Text:
        return "action_check_order_status"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_provide_order_status.")
        return []
