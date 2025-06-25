# Customer Care AI

This project implements a customer care chatbot using Rasa for natural language understanding and dialogue management.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Rasa 3.x

## Project Structure

```
.
├── actions/              # Custom Rasa actions
├── backend/
│   └── rasa/            # Rasa project files
│       ├── config.yml
│       ├── domain.yml
│       ├── data/
│       └── models/       # Trained models are saved here
├── web-interface/        # Web chat interface
└── docker-compose.yml    # Docker Compose configuration
```

## Training the Model

To train a new Rasa model, run:

```bash
# From the project root
cd backend/rasa
rasa train --fixed-model-name latest_rasa_model --out models
```

Or use the provided script:

```bash
./scripts/train_rasa.sh
```

## Running the Application

Start all services using Docker Compose:

```bash
docker-compose up -d --build
```

Services will be available at:
- Rasa Server: http://localhost:5005
- Web Interface: http://localhost:8080

## Development Workflow

1. Make changes to your NLU data, stories, or domain
2. Train a new model: `./scripts/train_rasa.sh`
3. Restart services: `docker-compose restart rasa`

## Model Management

- The model is saved as `latest_rasa_model.tar.gz` in `backend/rasa/models/`
- The Docker container is configured to automatically use the latest model
- Previous models are kept with timestamps in the filenames

## Troubleshooting

- If the model doesn't update, try rebuilding the container:
  ```bash
  docker-compose up -d --build rasa
  ```
  
- View Rasa logs:
  ```bash
  docker-compose logs -f rasa
  ```
