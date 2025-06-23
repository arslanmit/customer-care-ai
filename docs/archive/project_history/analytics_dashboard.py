#!/usr/bin/env python3
"""
RASA Analytics Dashboard
-----------------------
A Streamlit-based dashboard to visualize and analyze conversation metrics
from your RASA chatbot.
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

if len(sys.argv) == 1:
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

# Set page configuration
st.set_page_config(
    page_title="Customer Care AI Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Application title
st.title("Customer Care AI Analytics Dashboard")

# Sidebar for filters
st.sidebar.header("Filters")

# Date range selection
today = datetime.now()
default_start_date = today - timedelta(days=30)

start_date = st.sidebar.date_input("Start Date", default_start_date)
end_date = st.sidebar.date_input("End Date", today)

if start_date > end_date:
    st.error("Error: End date must be after start date")



@st.cache_data
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
    # Dynamic path resolution with fallbacks
    possible_paths = [
        # 1. Custom path if provided
        custom_path,
        # 2. Environment variable
        os.environ.get("CONVERSATION_DATA_PATH"),
        # 3. Relative paths from CWD
        os.path.join(os.getcwd(), "data/rasa_conversations.json"),
        os.path.join(os.getcwd(), "rasa_conversations.json"),
        # 4. Absolute path fallbacks
        "/Users/umitarslan/customer-care-ai/backend/data/rasa_conversations.json",
        os.path.expanduser("~/customer-care-ai/backend/data/rasa_conversations.json"),
    ]

    # Filter out None values
    valid_paths = [p for p in possible_paths if p]

    # Try each path until one works
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
        for err in errors[:3]:  # Show first 3 errors
            st.sidebar.error(err)
        return []


    # For direct JSON format with conversations array
    if "conversations" in data:
        return data["conversations"]

    # For TinyDB or Rasa tracker store format
    if isinstance(data, dict) and any(
        "events" in val for val in data.values() if isinstance(val, dict)
    ):
        conversations = []
        for tracker_id, tracker_data in data.items():
            # Skip non-conversation entries
            if not isinstance(tracker_data, dict) or "events" not in tracker_data:
                continue


            events = tracker_data.get("events", [])
            sender_id = tracker_data.get("sender_id", "unknown")

            # Process events into a more usable format
            messages = []
            for event in events:
                if not isinstance(event, dict):
                    continue

                event_type = event.get("event")
                timestamp = event.get("timestamp")

                if timestamp:
                    event_time = datetime.fromtimestamp(timestamp)
                else:
                    continue

                if event_type == "user":
                    messages.append(
                        {
                            "sender_id": sender_id,
                            "text": event.get("text", ""),
                            "timestamp": event_time,
                            "type": "user",
                        }
                    )
                elif event_type == "bot":
                    messages.append(
                        {
                            "sender_id": sender_id,
                            "text": event.get("text", ""),
                            "timestamp": event_time,
                            "type": "bot",
                        }
                    )
                elif event_type == "action":
                    messages.append(
                        {
                            "sender_id": sender_id,
                            "action": event.get("name", ""),
                            "timestamp": event_time,
                            "type": "action",
                        }
                    )

            if messages:
                start_time = min(msg["timestamp"] for msg in messages)
                end_time = max(msg["timestamp"] for msg in messages)

                conversations.append(
                    {
                        "conversation_id": tracker_id,
                        "sender_id": sender_id,
                        "messages": messages,
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration": (end_time - start_time).total_seconds(),
                        "num_user_messages": sum(
                            1 for msg in messages if msg["type"] == "user"
                        ),
                        "num_bot_messages": sum(
                            1 for msg in messages if msg["type"] == "bot"
                        ),
                        "num_actions": sum(
                            1 for msg in messages if msg["type"] == "action"
                        ),
                    }
                )

        return conversations

    # If it's not any known format, return raw data or empty list
    return data if isinstance(data, list) else []


# Load conversation data
conversations = load_conversation_data()

if not conversations:
    st.warning(
        (
            "No conversation data found. Please make sure your conversation data "
            "is available."
        )
    )
    st.info("Expected location: data/rasa_conversations.json")
    st.stop()

# Filter conversations based on date range
# Convert timestamp to datetime for filtering
for conv in conversations:
    if "timestamp" in conv and not isinstance(conv["timestamp"], datetime):
        # Convert from Unix timestamp to datetime if needed
        if isinstance(conv["timestamp"], (int, float)):
            conv["timestamp"] = datetime.fromtimestamp(conv["timestamp"])
        else:
            # Try to parse as string if not a timestamp
            try:
                conv["timestamp"] = datetime.fromisoformat(conv["timestamp"])
            except (ValueError, TypeError):
                conv["timestamp"] = datetime.now()  # Fallback

# Filter conversations based on timestamp
filtered_conversations = [
    conv
    for conv in conversations
    if "timestamp" in conv and start_date <= conv["timestamp"].date() <= end_date
]

# Calculate metrics from the conversation data format
# Process data to get required metrics
for conv in filtered_conversations:
    # Calculate number of user messages
    if "messages" in conv:
        # Count user messages in the messages array
        user_messages = [msg for msg in conv["messages"] if msg.get("type") == "user"]
        conv["num_user_messages"] = len(user_messages)

        # Duration is already in the data, but ensure it exists
        if "duration" not in conv:
            # If not present, calculate from timestamps if possible
            if len(conv["messages"]) >= 2:
                try:
                    first_msg_time = min(
                        msg.get("timestamp", 0) for msg in conv["messages"]
                    )
                    last_msg_time = max(
                        msg.get("timestamp", 0) for msg in conv["messages"]
                    )
                    conv["duration"] = last_msg_time - first_msg_time
                except (TypeError, ValueError):
                    conv["duration"] = 0
            else:
                conv["duration"] = 0
    else:
        conv["num_user_messages"] = 0
        conv["duration"] = 0

# Display basic metrics in a nice card layout
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Conversations",
        len(filtered_conversations),
        (
            "+{}%".format(
                round(
                    (len(filtered_conversations) / max(1, len(conversations))) * 100
                    - 100
                )
            )
            if len(conversations) > 0
            else "+0%"
        ),
    )

with col2:
    avg_msgs = (
        np.mean([conv.get("num_user_messages", 0) for conv in filtered_conversations])
        if filtered_conversations
        else 0
    )
    st.metric("Avg. Messages per Conversation", f"{avg_msgs:.1f}")

with col3:
    avg_duration = (
        np.mean([conv.get("duration", 0) for conv in filtered_conversations])
        if filtered_conversations
        else 0
    )
    st.metric("Avg. Duration (seconds)", f"{avg_duration:.1f}")

with col4:
    if filtered_conversations and any(
        "feedback" in conv for conv in filtered_conversations
    ):
        st.metric("Avg. User Rating", "N/A")

# Create charts with the data format
st.subheader("Conversation Analytics")

# Conversations by day
if filtered_conversations:
    # Extract dates from the timestamp field
    conversation_dates = [
        (
            conv["timestamp"].date()
            if isinstance(conv["timestamp"], datetime)
            else (
                datetime.fromtimestamp(conv["timestamp"]).date()
                if isinstance(conv["timestamp"], (int, float))
                else datetime.now().date()
            )
        )
        for conv in filtered_conversations
    ]

    date_counts = Counter(conversation_dates)

    date_df = pd.DataFrame(
        {"date": list(date_counts.keys()), "count": list(date_counts.values())}
    )

    date_df = date_df.sort_values("date")

    chart = (
        alt.Chart(date_df)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("count:Q", title="Number of Conversations"),
            tooltip=["date:T", "count:Q"],
        )
        .properties(title="Conversations by Day", height=300)
    )

    st.altair_chart(chart, use_container_width=True)

    # Create tabs for different analytics views
    tab1, tab2, tab3 = st.tabs(["User Messages", "Actions", "Conversation Details"])

    with tab1:
        # Extract all user messages
        all_user_messages = []
        for conv in filtered_conversations:
            for msg in conv["messages"]:
                if msg["type"] == "user":
                    all_user_messages.append(msg["text"])

        # Common user messages
        if all_user_messages:
            st.subheader("Most Common User Messages")
            message_counts = Counter(all_user_messages).most_common(10)
            message_df = pd.DataFrame(message_counts, columns=["Message", "Count"])

            chart = (
                alt.Chart(message_df)
                .mark_bar()
                .encode(
                    x=alt.X("Count:Q"),
                    y=alt.Y("Message:N", sort="-x"),
                    tooltip=["Message:N", "Count:Q"],
                )
                .properties(title="Top 10 User Messages", height=400)
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No user messages found in the selected date range.")

    with tab2:
        # Extract all actions
        all_actions = []
        for conv in filtered_conversations:
            for msg in conv["messages"]:
                if msg["type"] == "action" and "action" in msg:
                    all_actions.append(msg["action"])

        if all_actions:
            st.subheader("Most Common Actions")
            action_counts = Counter(all_actions).most_common(10)
            action_df = pd.DataFrame(action_counts, columns=["Action", "Count"])

            chart = (
                alt.Chart(action_df)
                .mark_bar()
                .encode(
                    x=alt.X("Count:Q"),
                    y=alt.Y("Action:N", sort="-x"),
                    tooltip=["Action:N", "Count:Q"],
                )
                .properties(title="Top 10 Bot Actions", height=400)
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No actions found in the selected date range.")
    with tab3:
        # Detailed conversation view
        st.subheader("Conversation Details")

        if filtered_conversations:
            # Process conversation data for table view
            table_data = []

            for i, conv in enumerate(filtered_conversations):
                # Extract user ID with fallbacks
                user_id = conv.get("user_id", conv.get("sender_id", f"user_{i}"))

                # Get timestamp
                timestamp = conv.get("timestamp", datetime.now())

                # Get duration, already calculated in previous step
                duration = conv.get("duration", 0)
                duration_display = (
                    f"{duration:.1f} sec" if duration < 60 else f"{duration/60:.1f} min"
                )

                # Get message count, already calculated in previous step
                msg_count = conv.get("num_user_messages", 0)

                # Get feedback if available
                feedback = conv.get("feedback", {})
                rating = feedback.get("rating", "N/A")

                # Add to table data
                table_data.append(
                    {
                        "ID": i + 1,
                        "User": user_id,
                        "Time": timestamp,
                        "Duration": duration_display,
                        "Messages": msg_count,
                        "Rating": rating,
                    }
                )

            # Create DataFrame and display
            conv_df = pd.DataFrame(table_data)
            st.dataframe(conv_df, use_container_width=True)


            st.subheader("Conversation Viewer")

            # Create a dropdown to select a conversation
            # Use a unique identifier for each conversation (index+1 in our case)
            conv_ids = [f"c{i+1}" for i in range(len(filtered_conversations))]
            conv_display = [
                f"Conversation {i+1} - {conv.get('user_id', 'Unknown User')}"
                for i, conv in enumerate(filtered_conversations)
            ]

            # Create a dictionary mapping display names to conversation indices
            conv_map = dict(zip(conv_ids, range(len(filtered_conversations))))

            # Select box with conversation IDs
            selected_id = st.selectbox(
                "Select conversation to view:",
                conv_ids,
                format_func=lambda x: f"Conversation {conv_map[x]+1}",
            )

            # Get the selected conversation based on the index
            if selected_id and selected_id in conv_map:
                selected_index = conv_map[selected_id]
                if 0 <= selected_index < len(filtered_conversations):
                    selected_conv = filtered_conversations[selected_index]

                    # Display conversation metadata
                    user_id = selected_conv.get(
                        "user_id", selected_conv.get("sender_id", "Unknown User")
                    )
                    st.write(f"User: {user_id}")

                    timestamp = selected_conv.get("timestamp", datetime.now())
                    st.write(f"Time: {timestamp}")

                    duration = selected_conv.get("duration", 0)
                    duration_display = (
                        f"{duration:.1f} seconds"
                        if duration < 60
                        else f"{duration/60:.1f} minutes"
                    )
                    st.write(f"Duration: {duration_display}")

                    # Display feedback if available
                    if "feedback" in selected_conv:
                        st.write(
                            f"Rating: {selected_conv['feedback'].get('rating', 'N/A')}/5"  # noqa: E501
                        )

                        if (
                            "comments" in selected_conv["feedback"]
                            and selected_conv["feedback"]["comments"]
                        ):
                            st.write(
                                f"Comments: {selected_conv['feedback']['comments']}"
                            )

                    # Display messages
                    st.write("### Conversation History")

                    if "messages" in selected_conv:
                        for msg in selected_conv["messages"]:
                            msg_type = msg.get("type", msg.get("role", ""))
                            msg_text = msg.get("text", msg.get("content", ""))

                            if msg_type == "user" or msg_type == "human":
                                st.markdown(f"**User:** {msg_text}")
                            elif msg_type == "bot" or msg_type == "assistant":
                                st.markdown(f"**Bot:** {msg_text}")
                            elif msg_type == "action":
                                st.markdown(f"**Action:** {msg_text}")
                    else:
                        st.info("No message history available for this conversation")
        else:
            st.info("No conversations found in the selected date range.")

else:
    st.info("No data found for the selected date range.")

# Add requirements section at the bottom
st.sidebar.markdown("---")
st.sidebar.subheader("Setup Requirements")
st.sidebar.code("pip install streamlit pandas matplotlib altair")
st.sidebar.markdown("Run dashboard: `streamlit run analytics_dashboard.py`")

# Footer
st.markdown("---")
st.markdown("Customer Care AI Analytics Dashboard | Built with Streamlit")
