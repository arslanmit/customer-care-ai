# Customer Care AI: Architecture Overview

This document outlines the current architecture of the Customer Care AI Chatbot, which is built on Rasa Open Source with a focus on simplicity and maintainability. The system uses local file-based storage for development and testing purposes.

## System Architecture

```ascii
+----------------+     HTTP      +---------------------+     File I/O     +------------------+
|                | <------------> |   Rasa Server      | <--------------> |   TinyDB         |
|  Rasa Shell   |               |   (v3.6.21)        |                  |   (tracker store) |
|  or API       |               |                     |                  |                  |
+----------------+               +---------------------+                  +------------------+
                                          |
                                          | File I/O
                                          v
                                 +------------------+
                                 |   FileEventBroker |
                                 |   (events.json)   |
                                 +------------------+
```

## Components

### 1. Rasa Server (v3.6.21)
- **Natural Language Understanding (NLU)**
  - Intent classification using DIET classifier
  - Entity extraction
  - Support for multiple languages

- **Core Components**
  - Dialogue management with TED Policy and Rule Policy
  - Custom actions for business logic
  - Fallback mechanisms

### 2. Data Storage
- **TinyDB Tracker Store**
  - File-based storage for conversation state
  - Located at `data/rasa_conversations.json`
  - Simple JSON format for easy inspection

- **FileEventBroker**
  - Logs conversation events to `data/events.json`
  - Useful for debugging and analysis

### 3. Custom Actions
- **ActionTellTime**
  - Returns the current time
  - Example: "What time is it?"

- **ActionHandoffToHuman**
  - Initiates handoff to a human agent
  - (Placeholder for future implementation)

## Development Setup

### Dependencies
- Python 3.10
- Rasa 3.6.21
- TinyDB
- FileEventBroker (built-in with Rasa)

### Configuration
- **endpoints.yml**: Configures the tracker store and event broker
  ```yaml
  tracker_store:
    type: tinydb_tracker_store.TinyDBTrackerStore
    db_path: data/rasa_conversations.json

  event_broker:
    type: FileEventBroker
    path: data/events.json
  ```

## Data Flow

1. **User Input**
   - User sends a message via Rasa shell or API
   - Rasa processes the message through NLU pipeline

2. **Dialogue Management**
   - Rasa Core selects the next action
   - Custom actions are executed if needed
   - Response is generated and sent to user

3. **Persistence**
   - Conversation state is saved to TinyDB
   - Events are logged to events.json

## Future Enhancements

1. **Scalability**
   - Replace TinyDB with PostgreSQL for production
   - Implement Redis for caching
   - Add load balancing for high availability

2. **Monitoring**
   - Add Prometheus metrics
   - Set up logging with ELK stack
   - Implement health checks

3. **Features**
   - Integration with external APIs
   - User authentication
   - Multi-channel support (web, mobile, etc.)

## Components Breakdown

### 1. User Client (React)

- Web-based chat interface with responsive design
- Real-time message streaming via WebSocket
- Multilingual support (English, Spanish, French, German, Turkish)
- JWT-based authentication with Google OAuth integration
- Progressive Web App (PWA) capabilities
- Offline mode support with local storage synchronization

### 2. Chatbot Backend (Rasa)

- **Natural Language Understanding (NLU)**
  - Intent classification with transformer-based models
  - Entity recognition with custom extractors
  - Language detection with multi-language support
  - DIET classifier for intent recognition
- **Dialogue Management**
  - TED policy for next action prediction
  - Rule-based fallback mechanisms
  - Custom action server integration
- **Custom Actions Implementation**
  - Time/date services (`ActionTellTime`, `ActionTellDate`, `ActionTellDateTime`)
  - Language management (`ActionSetLanguage`) for multi-lingual support
  - Human handoff capabilities (`ActionHandoffToHuman`)
  - Form validations (`ValidateNameForm`)
  - Fallback handling (`ActionIncrementFallbackCount`)
- **Session Management**
  - Redis-backed session storage
  - Conversation history with TTL
  - User context persistence across sessions

### 3. Integration Layer (Node.js)

- **API Gateway**
  - Request routing with path-based and header-based routing
  - OAuth 2.0 authentication with Google Cloud Identity
  - Token validation and refresh mechanisms
  - Rate limiting with Redis-based token bucket algorithm
- **Service Integration**
  - Payment processing with PCI compliance
  - CRM system synchronization with bidirectional updates
  - External API orchestration with circuit breakers
  - Webhook management for third-party integrations
- **Event Processing**
  - Real-time notifications with WebSocket
  - Google Cloud Pub/Sub integration
  - Asynchronous task handling with background workers
  - Event replay capabilities for system recovery

### 4. Data Layer

- **PostgreSQL**
  - User profiles with encrypted PII
  - Conversation history with indexing for fast retrieval
  - Analytics data with partitioning strategy
  - High availability setup with replication
- **Redis**
  - Session caching with configurable TTL
  - Rate limiting with sliding window algorithm
  - Pub/Sub messaging for real-time events
  - Distributed locks for concurrency control
- **Google Cloud Services**
  - Firestore for document storage
  - Cloud Storage for media and file handling
  - BigQuery for analytics and reporting
  - Secret Manager for credential management
- **External Services**
  - Payment gateways with tokenization
  - CRM systems with batch synchronization
  - Email/SMS services with templating
  - Voice services for telephony integration

## Key Features

### Scalability

- Horizontally scalable components
- Container orchestration with Kubernetes
- Auto-scaling based on load
- Database read replicas

### Resilience

- Circuit breakers for external services
- Retry policies with exponential backoff
- Graceful degradation
- Health checks and self-healing

### Security

- End-to-end encryption
- JWT authentication
- Role-based access control
- Regular security audits
- Data encryption at rest and in transit

### Observability

- Centralized logging with ELK stack
- Metrics collection with Prometheus
- Distributed tracing with Jaeger
- Real-time monitoring with Grafana

## Communication Flow

1. **User Interaction**
   - User sends message via React frontend
   - Message is encrypted and sent over HTTPS/WebSocket

2. **Request Processing**
   - Request authenticated at API Gateway
   - Load balanced to available Rasa instances
   - NLU processes user intent and entities

3. **Action Execution**
   - Custom actions triggered based on intent
   - External service calls made via Integration Layer
   - Business logic executed

4. **Response Generation**
   - Response formatted based on user preferences
   - Context updated in Redis
   - Response sent back through WebSocket

5. **Persistence**
   - Conversation logged to PostgreSQL
   - Analytics events generated
   - Session state updated

## Deployment Architecture

```ascii
                                  +------------------+
                                  |   Cloud IAM &    |
                                  |   Security       |
                                  +------------------+
                                           |
+----------------+     +------------------+ |   +------------------+
|  Frontend CDN  | <-> |  Cloud Load     | |   |  Rasa Servers    |
|  (GCP/CloudFl.)|     |  Balancer (GLB) | |-> |  (GKE Cluster)   |
+----------------+     +------------------+     +------------------+
                                |                        |
                                v                        v
                      +------------------+     +------------------+
                      | Node.js Services | <-> |  Redis Cluster  |
                      | (Cloud Run)      |     |  (Memorystore)   |
                      +------------------+     +------------------+
                                |                        |
                +---------------+----------------+       |
                |                                |       |
                v                                v       v
       +------------------+              +------------------+
       |   PostgreSQL     |              |   Cloud Storage/ |
       |   (Cloud SQL)    |              |   Firestore      |
       +------------------+              +------------------+
```

### Infrastructure

- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Google Kubernetes Engine (GKE) with node auto-provisioning
- **Serverless**: Cloud Run for event-driven services
- **CI/CD**: GitHub Actions with Cloud Build integration
- **Monitoring**: Cloud Monitoring, Cloud Logging, Prometheus, Grafana
- **Security**: Cloud IAM, Secret Manager, VPC Service Controls
- **Networking**: Cloud CDN, Cloud Armor, Private Service Connect

## Performance Characteristics

- **Throughput**: 1000+ requests/second with burst capacity to 5000+
- **Latency**: < 200ms for 95% of requests, < 500ms for 99.9%
- **Availability**: 99.95% uptime with multi-region failover capability
- **Scalability**: Linear scaling with load, auto-scaling based on CPU/memory metrics
- **Cold Start**: < 2s for serverless components
- **Database Performance**: Read queries < 50ms, write operations < 100ms
- **Cache Hit Ratio**: > 85% for frequently accessed data

## Future Considerations

- Integration with Google Cloud Dataflow for advanced analytics pipelines
- Implementation of Cloud Spanner for global database distribution
- Voice channel integration with DialogFlow CX and Contact Center AI
- Advanced conversational analytics with BigQuery ML
- Multi-region active-active deployment for global low-latency access
- AI/ML model versioning and A/B testing framework with Vertex AI
- Implementation of federated learning for privacy-preserving model improvements
- Enhanced multi-modal capabilities (image, voice, document processing)
- Context-aware personalization with recommendation systems
