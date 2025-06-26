from rasa_sdk import Action
from typing import Text

class ActionContactSupport(Action):
    def name(self) -> Text:
        return "action_contact_support"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="[Placeholder] This is action_contact_support.")
        return []
