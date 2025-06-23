# Backend

This directory contains the backend logic for the Customer Care AI project, including:

- Rasa custom actions (in `actions/`)
- Analytics dashboard code (`dashboard_app.py`, `data_loader.py`, `visualization.py`)
- Configuration, data handling, and utility scripts

## Structure

- `actions/` — Modular Rasa custom actions
- `dashboard_app.py` — Streamlit dashboard app entry point
- `data_loader.py` — Data loading and processing utilities
- `visualization.py` — Visualization and UI utilities for the dashboard

## Running the Dashboard

```sh
pip install streamlit pandas matplotlib altair
streamlit run dashboard_app.py
```

## Notes

- Place conversation data in `data/rasa_conversations.json` or set the `CONVERSATION_DATA_PATH` environment variable.
