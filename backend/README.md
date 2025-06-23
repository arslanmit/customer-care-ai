# Backend

This directory holds the Rasa server, custom actions and the optional FastAPI authentication API.

## Contents

- `actions/` – modular Rasa action classes
- `api/` – small FastAPI app for JWT auth
- `data/` – training examples and conversation logs
- `rasa/` – Rasa config and training data
- `tinydb_tracker_store.py` – local tracker store implementation
- `dashboard_app.py` – Streamlit analytics entry point

## Usage

Start the backend with Docker:
```bash
docker-compose up --build
```

For local development:
```bash
rasa run --enable-api &
rasa run actions &
```

The dashboard can be started with:
```bash
streamlit run dashboard_app.py
```
Conversation logs are read from `data/rasa_conversations.json` or the path specified by `CONVERSATION_DATA_PATH`.
