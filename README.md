# Customer Care AI

 

- **Rasa 3.6+ backend** with modular custom actions
- **TinyDB tracker store** for local conversation history
- **Streamlit dashboard** to explore conversation logs
- **Helper scripts** for development and deployment
- **Docker Compose and Cloud Run** configuration
- **Documentation in [`docs/`](docs/)**

 

1. Clone the repository and install Python dependencies:
   ```bash
   git clone https://github.com/your-username/customer-care-ai.git
   cd customer-care-ai
   pip install -r requirements.txt
  pip install rasa==3.6.21 rasa-sdk==3.6.21
  ```

   Train an initial model:
   ```bash
   cd backend
   rasa train
   cd ..
   ```
2. Copy `.env.example` to `.env` and adjust values.
3. Start services with Docker (or use `scripts/setup/setup.sh`):
   ```bash
  docker-compose up --build -d
  ```
  Rasa API is available at <http://localhost:5005> and the dashboard at <http://localhost:8501>.

4. Open `frontend/index.html` in your browser to try the minimal web chat interface.

For local development without Docker use `scripts/dev/start_dev.sh`. This script will set up the environment and start the necessary services.
Additional documentation can be found in the [`docs/`](docs/) folder.

## Environment Variables

Example settings:
```env
RASA_ENVIRONMENT=production
RASA_ACTIONS_PORT=5055
STREAMLIT_SERVER_PORT=8501
CONVERSATION_DATA_PATH=backend/data/rasa_conversations.json
JWT_SECRET=CHANGE_ME
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for more details.

## Testing

Run backend tests (none included by default):
```bash
pytest
```

## License

This project is licensed under the MIT License.

