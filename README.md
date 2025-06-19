# Customer Care AI Chatbot

A full-stack conversational AI chatbot built with Rasa (backend) and React (frontend), designed to handle customer service inquiries.

## Project Overview

This project implements an intelligent conversational agent that can:
- Handle basic greetings and farewells
- Collect user information using forms
- Respond to time inquiries
- Gracefully handle fallbacks when it doesn't understand user input

## Architecture

### Backend (Rasa)
- NLU pipeline with WhitespaceTokenizer, RegexFeaturizer, DIETClassifier, and FallbackClassifier
- Custom actions for telling time and jokes
- Form-based slot filling for collecting user information
- Conversation persistence with SQLite
- REST API with CORS support for frontend integration

### Frontend (React)
- Modern React application built with Vite
- Chat interface with message history
- Responsive design
- Environment-based configuration for backend URL

## Getting Started

### Prerequisites
- Python 3.8-3.10 (for Rasa compatibility)
- Node.js 18+
- Docker and Docker Compose (for containerized deployment)

### Local Development Setup

#### Backend Setup

1. Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train the Rasa model:
```bash
rasa train
```

4. Run the Rasa server:
```bash
# In one terminal
rasa run actions

# In another terminal
rasa run --enable-api --cors "*"
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

### Running with Docker Compose

For a complete containerized setup:

```bash
docker-compose up --build
```

This will start both the Rasa backend (available at http://localhost:5005) and the React frontend (available at http://localhost:8080).

## Testing

### Backend Tests

```bash
# Run Rasa tests
rasa test

# Run Python unit tests
python -m pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Deployment

The project is configured for deployment to Google Cloud Run with a CI/CD pipeline using GitHub Actions.

### Manual Deployment

1. Build Docker images:
```bash
# Backend
docker build -t gcr.io/<PROJECT_ID>/rasa-backend:latest -f Dockerfile .

# Frontend  
docker build -t gcr.io/<PROJECT_ID>/chat-frontend:latest -f frontend/Dockerfile .
```

2. Push images to Google Container Registry:
```bash
docker push gcr.io/<PROJECT_ID>/rasa-backend:latest
docker push gcr.io/<PROJECT_ID>/chat-frontend:latest
```

3. Deploy to Cloud Run:
```bash
# Backend
gcloud run deploy rasa-backend \
  --image gcr.io/<PROJECT_ID>/rasa-backend:latest \
  --platform managed --region <REGION> \
  --allow-unauthenticated

# Frontend
gcloud run deploy chat-frontend \
  --image gcr.io/<PROJECT_ID>/chat-frontend:latest \
  --platform managed --region <REGION> \
  --allow-unauthenticated \
  --update-env-vars REACT_APP_RASA_URL=<BACKEND_URL>
```

## CI/CD Pipeline

The GitHub Actions workflow in `.github/workflows/ci.yml` handles:

1. Running backend tests (Python/Rasa)
2. Running frontend tests (Jest)
3. On push to main: building Docker images and deploying to Google Cloud Run

## Project Structure

```
customer-care-ai/
├── actions/             # Custom Rasa actions
├── data/                # Training data (NLU, stories, rules)
├── models/              # Trained Rasa models
├── tests/               # Backend tests
├── frontend/            # React application
│   ├── src/             # React source code
│   └── tests/           # Frontend tests
├── .github/workflows/   # CI/CD configuration
├── docker-compose.yml   # Local development orchestration
├── Dockerfile           # Rasa backend container
└── entrypoint.sh        # Startup script for Rasa container
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
