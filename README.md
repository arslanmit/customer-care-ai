# Customer Care AI

Customer Care AI is a Rasa based chatbot with optional authentication API and an analytics dashboard. It supports multilingual intent recognition and can run locally with Docker Compose or be deployed to Google Cloud Run.

## Features

- **Rasa 3.6+ backend** with modular custom actions
- **TinyDB tracker store** for local conversation history
- **Streamlit dashboard** to explore conversation logs
- **Helper scripts** for development and deployment
- **Docker Compose and Cloud Run** configuration

## Getting Started

1. Clone the repository and install Python dependencies:
   ```bash
   git clone https://github.com/your-username/customer-care-ai.git
   cd customer-care-ai
   pip install -r requirements.txt
   ```
   Optionally download spaCy models:
   ```bash
   python scripts/download_models.py
   ./scripts/utils/install_requirements.sh
   ```
2. Copy `.env.example` to `.env` and adjust values.
3. Start services with Docker:
   ```bash
   docker-compose up --build -d
   ```
   Rasa API is available at <http://localhost:5005> and the dashboard at <http://localhost:8501>.

For local development without Docker use `scripts/dev/start_dev.sh`.

## Environment Variables

Example settings:
```env
RASA_ENVIRONMENT=production
RASA_ACTIONS_PORT=5055
STREAMLIT_SERVER_PORT=8501
CONVERSATION_DATA_PATH=backend/data/rasa_conversations.json
JWT_SECRET=change-me
```

## Project Layout
```
backend/    - Rasa actions and API
backend/rasa/ - Training data
dashboard/  - Streamlit app
scripts/    - Helper scripts (run `scripts/help.sh`)
docker-compose.yml
Dockerfile
```
See `ARCHITECTURE.md` for more details.

## Testing

Run backend tests (none included by default):
```bash
pytest
```

## License

This project is licensed under the MIT License.

