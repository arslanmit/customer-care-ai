# Architecture Overview

The core of the system is **Rasa**. Both the Rasa server and its action
server run inside a single Docker container so custom actions can execute
alongside the NLU and Core services. The container is built and deployed to
Google Cloud Run via a Cloud Build trigger. Source code lives in a private
GitHub repository.

```
+-------------+        push         +-------------+       build/deploy
| Developer   | ----------------->  | GitHub Repo | ----------------->
+-------------+                     +-------------+                    
                                        |  Cloud Build Trigger       
                                        v
                                 +----------------+
                                 | Cloud Build    |
                                 +----------------+
                                        |
                                        v
                                 +----------------+
                                 | Cloud Run      |
                                 +----------------+
```
Client --> Rasa REST API --> Rasa (NLU+Core + Actions)
```

Rasa sits at the centre of all user interactions. The lightweight web chat or any other client simply posts messages to the REST endpoint.

## Components

| Component       | Purpose |
| --------------- | --------------------------------------------------------------- |
| Rasa (NLU+Core) | Handles intent detection and dialogue management. |
| Action Server   | Runs inside the same container to execute custom actions. |
| TinyDB Tracker  | Persists conversation state to `data/rasa_conversations.json`. |
| FileEventBroker | Writes an append-only event log to `data/events.json`. |
| Streamlit       | Visualises conversation logs for analytics. |
| Cloud Build     | Builds the Docker image and deploys to Cloud Run. |


External clients (a simple HTML page or a future React app) communicate with Rasa via the REST channel. An optional FastAPI service supplies JWT-based authentication if required.

### Rasa Settings

The Rasa service uses the following configuration snippets in
`backend/rasa/endpoints.yml`:

```yaml
tracker_store:
  type: tinydb_tracker_store.TinyDBTrackerStore
  db_path: data/rasa_conversations.json

event_broker:
  type: FileEventBroker
  path: data/events.json
```

This ensures conversation history survives restarts and all events are stored for
later analysis.

### Build Window

The architecture is intentionally minimal to support a complete prototype within
12 hours.  Development occurs locally with WindSurf IDE.  Pushing to GitHub
triggers Cloud Build which builds the Docker image and deploys to Cloud Run.
No GitHub Actions are used.

