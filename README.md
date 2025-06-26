# Customer Care AI

This project implements a customer care chatbot using Rasa for natural language understanding and dialogue management.

## Key Features

- **Rasa 3.0+ Compatible**: Updated slot handling using explicit slot setting
- **Modular Action Design**: Easy to extend with new functionality
- **Docker Support**: Easy deployment with Docker Compose
- **Comprehensive Testing**: Unit tests for all slot extraction actions

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Rasa 3.x

## Slot Handling

This project uses explicit slot setting in Rasa 3.0+ instead of the deprecated auto-fill mechanism. Slots are set using custom actions that extract entities from user messages and explicitly set slot values.

### Key Components

1. **Slot Definitions** in `domain.yml`
   - Each slot is defined with a custom mapping that specifies which action should handle its extraction
   - Example:
     ```yaml
     slots:
       order_number:
         type: text
         influence_conversation: true
         mappings:
           - type: custom
             action: action_extract_order_number
     ```

2. **Slot Extraction Actions** in `actions/action_extract_slots.py`
   - Each slot has a dedicated action that extracts the value from the latest user message
   - Actions return `SlotSet` events to update the conversation state

3. **Rules** in `data/rules.yml`
   - Rules define when slot extraction actions should be triggered
   - Example:
     ```yaml
     - rule: Set order number
       steps:
         - intent: provide_order_number
         - action: action_extract_order_number
     ```

### Adding a New Slot

1. Add the slot definition to `domain.yml`
2. Create a new action in `action_extract_slots.py`
3. Add a rule in `data/rules.yml` to trigger the extraction action
4. Update the stories if needed to include the slot setting action

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
