# Customer Care AI Chatbot

A full-stack conversational AI chatbot built with Rasa (backend) and React (frontend), designed to handle customer service inquiries with multilingual support and advanced conversation management.

## 🚀 Key Features

- **Multilingual Support**: English, Spanish, French, German, and Turkish
- **Advanced Conversation Flow**: Stateful conversations with context management
- **Production-Ready**: Containerized with Docker and Kubernetes support
- **Scalable Architecture**: Microservices-based design with Redis for caching
- **Monitoring**: Integrated with Prometheus and Grafana
- **CI/CD**: Automated testing and deployment with GitHub Actions

## 🏗️ Project Structure

```
customer-care-ai/
├── .github/              # GitHub Actions workflows
├── actions/              # Custom Rasa actions
│   └── actions.py        # Action server implementation
├── backend/              # Rasa backend
│   ├── data/             # NLU training data, stories, rules
│   ├── models/           # Trained Rasa models
│   ├── tests/            # Backend tests
│   ├── config.yml        # Rasa configuration
│   ├── credentials.yml   # Channel credentials
│   ├── domain.yml        # Domain definition
│   └── endpoints.yml     # Endpoint configurations
├── frontend/             # React application
│   ├── public/           # Static files
│   ├── src/              # React source code
│   └── tests/            # Frontend tests
├── monitoring/           # Monitoring setup
│   ├── prometheus/       # Prometheus config
│   └── grafana/          # Grafana dashboards
├── scripts/              # Utility scripts
├── .env.example         # Environment variables template
├── docker-compose.yml    # Local development
├── Dockerfile           # Production Dockerfile
├── requirements.txt     # Python dependencies
└── setup.sh            # Setup script
```

## 🛠️ Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Redis
- PostgreSQL

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/customer-care-ai.git
cd customer-care-ai
```

### 2. Set up the environment

```bash
# Make setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 3. Configure environment variables

Copy the example environment file and update the values:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start the services

Using Docker Compose (recommended):

```bash
docker-compose up -d
```

Or manually:

```bash
# Start Redis
redis-server &


# Start Rasa actions server
rasa run actions &


# Start Rasa API server
rasa run --enable-api --cors "*" &


# Start frontend (from frontend directory)
cd frontend
npm install
npm run dev
```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_actions.py -v

# Run with coverage
pytest --cov=actions tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Docker Compose (Production)

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Kubernetes (GKE)

```bash
# Set up kubectl context
gcloud container clusters get-credentials CLUSTER_NAME --region REGION

# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### Google Cloud Run

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/customer-care-ai

# Deploy to Cloud Run
gcloud run deploy customer-care-ai \
  --image gcr.io/PROJECT_ID/customer-care-ai \
  --platform managed \
  --region REGION \
  --allow-unauthenticated
```

## 📊 Monitoring

Access monitoring dashboards:

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Project Link: [https://github.com/yourusername/customer-care-ai](https://github.com/yourusername/customer-care-ai)
