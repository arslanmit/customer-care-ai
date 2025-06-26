from rasa_sdk import Action
from typing import Text

class ActionReturnItem(Action):
    def name(self) -> Text:
        return "action_return_item"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_return_item.")
        return []
