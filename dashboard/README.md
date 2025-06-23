# Dashboard

This Streamlit app lets you explore conversation logs produced by Rasa.

Run it from the project root:
```bash
streamlit run dashboard/dashboard_app.py
```

The app loads conversations from `CONVERSATION_DATA_PATH` (defaults to `backend/data/rasa_conversations.json`).

Main files:
- `dashboard_app.py` – Streamlit entry point
- `data_loader.py` – helpers for reading log files
- `visualization.py` – tables and charts
