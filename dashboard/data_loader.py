import json
import os
import streamlit as st
from datetime import datetime

def load_conversation_data(custom_path=None):
    """Load and process the conversation data.

    This function dynamically locates and loads conversation data using the following
    priority:
    1. Custom path provided as parameter
    2. Path from environment variable CONVERSATION_DATA_PATH
    3. Relative path to current working directory
    4. Default absolute path as fallback

    Args:
        custom_path: Optional custom path to the conversation data file

    Returns:
        List of conversation data dictionaries
    """
    possible_paths = [
        custom_path,
        os.environ.get("CONVERSATION_DATA_PATH"),
        os.path.join(os.getcwd(), "data/rasa_conversations.json"),
        os.path.join(os.getcwd(), "rasa_conversations.json"),
        "/Users/umitarslan/customer-care-ai/backend/data/rasa_conversations.json",
        os.path.expanduser("~/customer-care-ai/backend/data/rasa_conversations.json"),
    ]
    valid_paths = [p for p in possible_paths if p]
    data = None
    errors = []
    for path in valid_paths:
        try:
            with open(path, "r") as f:
                data = json.load(f)
                st.sidebar.success(f"✅ Loaded data from: {os.path.basename(path)}")
                break
        except FileNotFoundError:
            errors.append(f"File not found: {path}")
            continue
        except json.JSONDecodeError:
            errors.append(f"Invalid JSON in: {path}")
            continue
        except Exception as e:
            errors.append(f"Error loading {path}: {str(e)}")
            continue
    if data is None:
        st.sidebar.error("⚠️ Failed to load conversation data!")
        for err in errors[:3]:
            st.sidebar.error(err)
        return []
    if "conversations" in data:
        return data["conversations"]
    if isinstance(data, dict) and any(
        "events" in val for val in data.values() if isinstance(val, dict)
    ):
        conversations = []
        for tracker_id, tracker_data in data.items():
            if not isinstance(tracker_data, dict) or "events" not in tracker_data:
                continue
            events = tracker_data.get("events", [])
            sender_id = tracker_data.get("sender_id", "unknown")
            messages = []
            for event in events:
                if event.get("event") == "user":
                    messages.append({
                        "type": "user",
                        "text": event.get("text", "")
                    })
                elif event.get("event") == "bot":
                    messages.append({
                        "type": "bot",
                        "text": event.get("text", "")
                    })
                elif event.get("event") == "action":
                    messages.append({
                        "type": "action",
                        "text": event.get("name", "")
                    })
            conversations.append({
                "user_id": sender_id,
                "messages": messages,
                "timestamp": tracker_data.get("latest_event_time", datetime.now()),
                "duration": tracker_data.get("duration", 0),
                "feedback": tracker_data.get("feedback", {}),
            })
        return conversations
    return []
