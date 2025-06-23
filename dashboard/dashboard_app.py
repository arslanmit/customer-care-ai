import streamlit as st
from datetime import datetime, timedelta
from . import data_loader
from . import visualization

st.set_page_config(
    page_title="Customer Care AI Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Customer Care AI Analytics Dashboard")

st.sidebar.header("Filters")
today = datetime.now()
default_start_date = today - timedelta(days=30)

start_date = st.sidebar.date_input("Start Date", default_start_date)
end_date = st.sidebar.date_input("End Date", today)

if start_date > end_date:
    st.error("Error: End date must be after start date")

conversations = load_conversation_data()

# Filter conversations by date range if timestamps are available
if conversations:
    def parse_timestamp(ts):
        if isinstance(ts, (int, float)):
            # Assume UNIX timestamp
            return datetime.fromtimestamp(ts)
        try:
            return datetime.fromisoformat(str(ts))
        except Exception:
            return today  # fallback

    filtered_conversations = [
        conv for conv in conversations
        if "timestamp" in conv and start_date <= parse_timestamp(conv["timestamp"]).date() <= end_date
    ]
else:
    filtered_conversations = []

show_conversation_table(filtered_conversations)
show_conversation_viewer(filtered_conversations)

st.sidebar.markdown("---")
st.sidebar.subheader("Setup Requirements")
st.sidebar.code("pip install streamlit pandas matplotlib altair")
st.sidebar.markdown("Run dashboard: `streamlit run dashboard_app.py`")

st.markdown("---")
st.markdown("Customer Care AI Analytics Dashboard | Built with Streamlit")
