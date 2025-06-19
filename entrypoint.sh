#!/bin/bash
# entrypoint.sh for Rasa container

# Start Rasa action server in background
rasa run actions --port 5055 &

# Start Rasa server (enable API and CORS, use PORT env if provided by platform)
rasa run -m models --enable-api --cors "*" --port ${PORT:-5005} --debug
