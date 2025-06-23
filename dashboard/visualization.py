import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

def show_conversation_table(conversations):
    table_data = []
    for i, conv in enumerate(conversations):
        table_data.append({
            "ID": f"c{i+1}",
            "User": conv.get("user_id", "Unknown User"),
            "Timestamp": conv.get("timestamp", datetime.now()),
            "Duration": conv.get("duration", 0),
            "Num Messages": len(conv.get("messages", [])),
        })
    conv_df = pd.DataFrame(table_data)
    st.dataframe(conv_df, use_container_width=True)

def show_conversation_viewer(conversations):
    st.subheader("Conversation Viewer")
    if not conversations:
        st.info("No conversations found in the selected date range.")
        return
    conv_ids = [f"c{i+1}" for i in range(len(conversations))]
    conv_map = dict(zip(conv_ids, range(len(conversations))))
    selected_id = st.selectbox(
        "Select conversation to view:",
        conv_ids,
        format_func=lambda x: f"Conversation {conv_map[x]+1}",
    )
    if selected_id and selected_id in conv_map:
        selected_index = conv_map[selected_id]
        if 0 <= selected_index < len(conversations):
            selected_conv = conversations[selected_index]
            user_id = selected_conv.get("user_id", selected_conv.get("sender_id", "Unknown User"))
            st.write(f"User: {user_id}")
            timestamp = selected_conv.get("timestamp", datetime.now())
            st.write(f"Time: {timestamp}")
            duration = selected_conv.get("duration", 0)
            duration_display = (
                f"{duration:.1f} seconds" if duration < 60 else f"{duration/60:.1f} minutes"
            )
            st.write(f"Duration: {duration_display}")
            if "feedback" in selected_conv:
                st.write(f"Rating: {selected_conv['feedback'].get('rating', 'N/A')}/5")
                if "comments" in selected_conv["feedback"] and selected_conv["feedback"]["comments"]:
                    st.write(f"Comments: {selected_conv['feedback']['comments']}")
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
