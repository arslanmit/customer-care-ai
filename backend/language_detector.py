from typing import Any, Dict, List, Text, Type

from langdetect import detect, LangDetectException
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import METADATA


@DefaultV1Recipe.register("language_detector.LanguageDetector")
class LanguageDetector(GraphComponent):
    """A simple component that detects the incoming message language using langdetect
    and stores it on the message under the key `detected_language` as well as inside
    message metadata. It can later be read by policies or custom actions.
    """

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        # No configurable params for now; could add whitelist etc.
        return {}

    def __init__(self, config: Dict[Text, Any]) -> None:
        self.config = config

    @classmethod
    def required_components(cls) -> List[Type[GraphComponent]]:  # type: ignore[override]
        # This component runs before tokenization, so no requirements.
        return []

    def process(self, messages: List[Message]) -> List[Message]:  # type: ignore[override]
        for message in messages:
            text = message.get("text", "")
            detected_lang = "en"
            try:
                detected_lang = detect(text) if text else "en"
            except LangDetectException:
                # default to English on failure
                detected_lang = "en"
            # Store on message object
            message.set("detected_language", detected_lang, add_to_output=True)
            # Persist in metadata so that the downstream custom actions / front-end can access
            meta = message.get(METADATA, {}) or {}
            meta["language"] = detected_lang
            message.set(METADATA, meta)
        return messages
