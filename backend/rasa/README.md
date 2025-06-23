# Rasa Training Data

This directory stores all YAML files used to train the assistant.

- `data.yml` – main file that imports the individual data files
- `nlu*.yml` – example utterances and entities
- `rules_*.yml`, `stories_*.yml` – conversation flows
- `domain.yml` – intents, entities and responses

When adding new files reference them inside `data.yml` so Rasa picks them up.

To validate the dataset run:
```bash
rasa data validate --data backend/rasa/data.yml
```
Train a model with:
```bash
rasa train --data backend/rasa/data.yml
```
