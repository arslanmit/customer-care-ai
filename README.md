# Customer Care AI

A production-ready conversational AI chatbot built with Rasa (backend) and React (frontend), designed to handle customer service inquiries with multilingual support and advanced conversation management. The application is containerized with Docker for easy deployment and scaling.

[![Rasa Version](https://img.shields.io/badge/Rasa-3.6%2B-5a17ee.svg)](https://rasa.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Key Features

- **Multilingual Support**: Native support for multiple languages
- **Advanced Conversation Flow**: Stateful conversations with Rasa
- **Production-Ready**: Containerized with Docker for easy deployment
- **Monitoring**: Built-in support for Prometheus and Grafana
- **Scalable**: Designed for horizontal scaling

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/customer-care-ai.git
   cd customer-care-ai
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

4. **Access the application**
   - Frontend: http://your-domain.com
   - Admin Dashboard: http://your-domain.com/admin
   - Grafana: http://your-domain.com/grafana
   - Prometheus: http://your-domain.com/prometheus

## 📦 Production Deployment

### Kubernetes (Recommended for Production)

1. **Set up a Kubernetes cluster**
   ```bash
   gcloud container clusters create customer-care-ai \
     --num-nodes=3 \
     --machine-type=e2-medium \
     --zone=us-central1-a
   ```

2. **Deploy the application**
   ```bash
   kubectl apply -f k8s/
   ```

### Environment Variables

Required environment variables:

```
# Application
NODE_ENV=production
TZ=UTC

# Rasa
RASA_ENVIRONMENT=production
RASA_ACTIONS_PORT=5055
RASA_MODEL=./models

# Database
POSTGRES_USER=rasa
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=rasa

# Monitoring
PROMETHEUS_METRICS_PORT=9090
GRAFANA_PORT=3001
```

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)

## 🔒 Security

- All traffic is encrypted with TLS
- JWT authentication for API access
- Regular security updates
- Rate limiting enabled

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏗️ Project Structure

```text
customer-care-ai/​
├── .github/                  # GitHub Actions workflows
├── backend/                  # Rasa backend implementation
│   ├── actions/              # Custom Rasa actions (incl. ActionAskOrderNumber, ActionTellJoke, etc.)
│   ├── api/                  # API endpoints (FastAPI)
│   ├── data/                 # NLU data, stories, rules
│   ├── models/               # Trained Rasa models
│   ├── results/              # Test and analytics reports
│   └── tests/                # Backend tests
├── frontend/                 # React 18 + Vite app
│   ├── src/                  # Main source code
│   │   ├── Analytics.jsx     # Analytics dashboard
│   │   ├── Feedback.jsx      # Feedback modal
│   │   ├── Auth.jsx          # Supabase Auth context/hooks
│   │   ├── Chatbot.jsx       # Main chatbot UI
│   │   └── ...
│   ├── public/               # Static files
│   ├── Dockerfile*           # Frontend Docker configs
│   ├── package.json          # Frontend deps/scripts
│   ├── vite.config.js        # Vite config
│   └── ...
├── monitoring/               # Monitoring setup
│   ├── grafana/              # Grafana dashboards
│   └── prometheus/           # Prometheus config
├── scripts/                  # Utility scripts
│   ├── generate-secrets.sh   # Secure secret generation
│   └── monitor_logs.sh       # Log monitoring utility
├── supabase/                 # Supabase migrations & DB setup
│   └── migrations/           # SQL migrations (event logging, RLS, analytics)
├── .env.example              # Env var template
├── docker-compose.yml        # Local dev
├── docker-compose.prod.yml   # Production
├── Dockerfile                # Backend Dockerfile
├── requirements.txt          # Python deps
├── setup.sh                  # Project setup script
└── setup_local.sh            # Local dev setup
```

_Note: See `ARCHITECTURE.md` for a detailed architecture overview._

## 🛠️ Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Python 3.10+ (for backend/local dev)
- Node.js 18+ (for frontend dev)
- React 18+
- Vite (bundler, included in frontend)
- Chart.js (frontend analytics)
- Supabase account (for DB/auth)
- Git
- (Optional) Google Cloud CLI for GKE/Cloud Run deployment

## 🧪 Testing & Code Quality

Run the test suite:

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
npm run lint
npm run format
```

- **Vitest**: Unit and integration tests for frontend
- **ESLint**: Linting for React code
- **Prettier**: Code formatting
- **Test Reports**: Backend intent/story analytics in `backend/results/`

## 🚀 Deployment

### Production Deployment

1. Build and start the production containers:

   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. Set up monitoring:

   - Access Grafana at [http://your-domain:3001](http://your-domain:3001)
   - Default credentials: admin/admin (change immediately after first login)

## 📊 Monitoring

The application includes built-in monitoring with:

- **Prometheus** for metrics collection
- **Grafana** for visualization
- **Health check endpoints** at `/health`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Rasa](https://rasa.com/) for the open-source conversational AI framework
- [React](https://reactjs.org/) for the frontend library
- [Supabase](https://supabase.com/) for the open-source Firebase alternative
- [Docker](https://www.docker.com/) for containerization

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Quick Start

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

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Generate secure secrets using the provided script:

   ```bash
   chmod +x scripts/generate-secrets.sh
   ./scripts/generate-secrets.sh
   ```

3. Update remaining configuration in `.env`:

   ```bash
   # Edit .env with your configuration
   # Set appropriate values for:
   # - Database credentials
   # - API keys
   # - Domain names
   # - Email settings
   # - Any other environment-specific settings
   ```

4. Set secure file permissions:

   ```bash
   chmod 600 .env
   chmod 700 scripts/
   ```

> **Security Note**: Never commit the `.env` file to version control. It's already included in `.gitignore`.

### 4. Start the services

Using Docker Compose (recommended for production):

```bash
# Build and start all services in detached mode
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services if needed
docker-compose -f docker-compose.prod.yml up -d --scale rasa=2 --scale actions=2
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

## Testing

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

## Security Best Practices

### Security Features

- **Secure by Default**:
  - All services run as non-root users
  - Read-only filesystems where possible
  - Minimal container images
  - Automatic security updates

- **Data Protection**:
  - Encryption at rest and in transit
  - Secure secret management
  - Regular backups with encryption

- **Compliance**:
  - GDPR-ready data handling
  - Configurable data retention policies
  - Audit logging for all sensitive operations

### Security Controls

1. **Container Security**:
   - Image signing and verification
   - Runtime security monitoring
   - Resource constraints and limits

2. **Network Security**:
   - Network segmentation
   - TLS 1.2+ for all communications
   - Web Application Firewall (WAF) ready

3. **Access Control**:
   - Role-Based Access Control (RBAC)
   - Multi-factor authentication (MFA) support
   - IP whitelisting

### Incident Response

- **Monitoring**:
  - Real-time security monitoring
  - Anomaly detection
  - Automated alerts

- **Response**:
  - Incident response plan
  - Automated remediation
  - Forensic capabilities

### Security Documentation

- [Security Policy](SECURITY.md)
- [Incident Response Plan](docs/INCIDENT_RESPONSE.md)
- [Compliance Documentation](docs/COMPLIANCE.md)

### Security Updates

- Regular dependency updates
- Security patch management
- CVE monitoring and response

## Development

### Backend

- Rasa actions: Add new actions in `backend/actions/`
- Intent analytics: Results in `backend/results/`
- Supabase event logging: All conversation events and feedback are logged (see `supabase/migrations/`)
- Security: RLS enabled on event tables, policies for read/insert

### Frontend

- React 18 + Vite
- Analytics dashboard: `src/Analytics.jsx`
- Feedback modal: `src/Feedback.jsx`
- Supabase Auth: `src/Auth.jsx`
- Code quality: ESLint, Prettier, Vitest

### Scripts & Utilities

- `scripts/generate-secrets.sh`: Generate strong secrets for env
- `scripts/monitor_logs.sh`: Real-time log monitoring
- DB migrations: `supabase/migrations/`

### Configuration

- Environment variables: `.env` (see `.env.example`)
- Supabase: Set up project, apply migrations, configure RLS

_Note: See `ARCHITECTURE.md` for more details on the system design._

## Security Monitoring

### Logging

- Structured logging with security context
- Centralized log management
- Long-term log retention

### Alerting

- Real-time security alerts
- Escalation policies
- On-call rotations

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

## Contact

Project Link: [GitHub Repository](https://github.com/yourusername/customer-care-ai)

## Secure Configuration

- **Secrets Management**:
  - All secrets are stored in `.env` (never committed to version control)
  - Use the provided `scripts/generate-secrets.sh` to generate strong secrets
  - Consider using a secrets manager in production (e.g., AWS Secrets Manager, HashiCorp Vault)

- **Docker Security**:
  - Containers run as non-root users
  - Read-only filesystems where possible
  - Minimal base images
  - Regular security scanning of container images

## Network Security

- **TLS/SSL**:
  - Enable HTTPS with valid certificates (use Let's Encrypt in production)
  - Configure HSTS headers
  - Enable TLS 1.2+ only

- **Firewall Rules**:
  - Restrict access to management interfaces
  - Use VPC peering for internal communication
  - Implement network policies in Kubernetes

## Authentication & Authorization

- **JWT Authentication**:
  - Secure token storage
  - Short-lived access tokens
  - Secure cookie settings

- **Rate Limiting**:
  - Implemented at the API gateway level
  - Configurable rate limits per endpoint

## Deployment

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

## Monitoring & Analytics

- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **Grafana**: [http://localhost:3001](http://localhost:3001) (admin/admin)
- **Analytics Dashboard**: In-app (frontend) for intent distribution, response times, etc.
- **Log Monitoring**: `scripts/monitor_logs.sh` (real-time error/warning tailing)
- **Event Logging**: Conversation and feedback events are stored in Supabase (see `supabase/migrations/` for schema and RLS policies)
