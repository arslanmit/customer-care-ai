# Customer Care AI

An enterprise-ready conversational AI chatbot built with Rasa (backend), designed to handle customer service inquiries with enhanced fallback strategies, advanced analytics, . The application can be deployed on-premise or in the cloud with Google Cloud integration.

[![Rasa Version](https://img.shields.io/badge/Rasa-3.6%2B-5a17ee.svg)](https://rasa.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Google Cloud Ready](https://img.shields.io/badge/Google%20Cloud-Ready-4285F4.svg)](https://cloud.google.com/)

## 🚀 Key Features

- **Enhanced Fallback Strategies**: Multi-stage fallbacks with configurable confidence thresholds
- **Multilingual Support**: Native support for multiple languages with automatic detection
- **Advanced Analytics Dashboard**: Real-time metrics and conversation insights
- **RASA Watchdog**: Automatic monitoring and self-healing for high availability
- **Google Cloud Integration**: Built-in deployment support for Google Cloud Run and Storage

- **High Availability**: Auto-restart capability with configurable retry limits

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.10+ (for local development)
- Google Cloud SDK (for cloud deployment)

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/customer-care-ai.git
   cd customer-care-ai
   ```

2. **Set up Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Download and install language models**

   ```bash
   # Download the models
   python scripts/download_models.py
   
   # Install requirements including the downloaded models
   ./scripts/install_requirements.sh
   ```

5. **Start the application**

   ```bash
   docker-compose up --build -d
   ```

6. **Access the application**
   - API: [http://localhost:5005](http://localhost:5005)
   - Analytics Dashboard: [http://localhost:8501](http://localhost:8501)

## 🔧️ Configuration

### Environment Variables

Key environment variables:

```env
# Application
NODE_ENV=production
TZ=UTC

# Rasa
RASA_ENVIRONMENT=production
RASA_ACTIONS_PORT=5055
RASA_MODEL=./models

# Analytics Dashboard
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
CONVERSATION_DATA_PATH=/path/to/data/rasa_conversations.json

# Google Cloud
GCLOUD_PROJECT=your-project-name
GCLOUD_BUCKET=your-bucket-name
```

## 🔍 Enhanced Components

### Enhanced Fallback Strategies

The enhanced fallback system provides improved handling of low-confidence and ambiguous user intents:

- **Multi-stage fallbacks**: Progressive fallback responses to guide users
- **Configurable thresholds**: Adjust confidence thresholds for different domains
- **Intent clarification**: Ask clarifying questions when multiple intents have similar confidence scores
- **Fallback forms**: Collect additional information during fallback scenarios

Configuration is in `backend/config.yml` under the `policies` section.

### Analytics Dashboard

The analytics dashboard provides real-time insights into your chatbot's performance:

- **Real-time metrics**: Track conversation volume, user satisfaction, and intent distribution
- **Dynamic data loading**: Automatically locates and processes conversation data from multiple sources
- **Conversation viewer**: Interactive interface to review full conversation history
- **Data filters**: Filter conversations by date range, intent, or feedback score

Access the dashboard at [http://localhost:8501](http://localhost:8501) when running locally.

### RASA Watchdog

The watchdog script ensures high availability of your chatbot services:

- **Automatic monitoring**: Continuously checks the health of RASA and action servers
- **Self-healing**: Automatically restarts services that become unresponsive
- **Configurable retries**: Set retry limits and cooldown periods
- **Detailed logging**: Colorized logs with timestamps for troubleshooting

The watchdog script is located at `backend/rasa_watchdog.sh`.

### Google Cloud Integration

Built-in support for Google Cloud deployment and storage:

- **Cloud Storage buckets**: Automatic setup with lifecycle policies for logs and models
- **Cloud Run deployment**: Scripts for deploying to serverless environments
- **Authentication**: Pre-configured for seamless integration with Google Cloud services
- **Logging integration**: Structured logging compatible with Cloud Logging

Configuration is in `backend/gcloud_integration.sh`.

## 📚 Documentation

- [API Reference](docs/API.md)

## 🔒 Security

- JWT authentication for API access
- Rate limiting enabled
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Scripts & Utilities

All scripts for development, deployment, and maintenance are organized under the `scripts/` directory:

- `scripts/dev/` — Development utilities (start, stop, monitor services, etc.)
- `scripts/deployment/` — Deployment scripts (GCP, Cloud Run, secrets, etc.)
- `scripts/utils/` — Utility and fix scripts (dependency fixes, test helpers, etc.)

To see all available scripts and their descriptions, run:

```bash
./scripts/help.sh
```

Each script supports `-h` or `--help` for usage information and options.

## 🏗️ Project Structure

```text
customer-care-ai/​
├── .github/                    # GitHub Actions workflows
├── backend/                    # Rasa backend implementation
│   ├── actions/                # Custom Rasa actions
│   ├── api/                    # API endpoints (FastAPI)
│   ├── data/                   # NLU data, stories, rules
│   │   └── rasa_conversations.json # Conversation logs for analytics
│   ├── models/                 # Trained Rasa models
│   ├── results/                # Test and analytics reports
│   ├── fallback_config/        # Enhanced fallback strategies configuration
│   │   └── enhanced_fallbacks.yml # Enhanced fallback definitions
│   ├── analytics_dashboard.py  # Analytics dashboard
│   └── tests/                  # Backend tests
├── monitoring/                 # Monitoring setup
│   ├── grafana/                # Grafana dashboards
│   └── prometheus/             # Prometheus config
├── scripts/                    # Utility scripts
│   ├── generate-secrets.sh     # Secure secret generation
│   └── monitor_logs.sh         # Log monitoring utility
├── logs/                       # System and application logs
│   └── gcloud_setup.log        # Google Cloud setup logs
├── .env.example                # Env var template
├── docker-compose.yml          # Local dev
├── docker-compose.prod.yml     # Production
├── Dockerfile                  # Backend Dockerfile
├── requirements.txt            # Python deps
├── setup.sh                    # Project setup script
└── setup_local.sh              # Local dev setup
```

_Note: See `ARCHITECTURE.md` for a detailed architecture overview._

## 🛠️ Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Python 3.10+ (for backend/local dev)
-  account (for DB/auth)
- Git
- (Optional) Google Cloud CLI for GKE/Cloud Run deployment

## 🧪 Testing & Code Quality

Run the test suite:

```bash
# Backend tests
cd backend
pytest

npm run test
npm run lint
npm run format
```

- **ESLint**: Linting for React code
- **Prettier**: Code formatting
- **Test Reports**: Backend intent/story analytics in `backend/results/`

## 🚀 Deployment

### Production Deployment

1. Build and start the production containers:

   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. Start the RASA Watchdog for high availability:

   ```bash
   cd backend
   chmod +x rasa_watchdog.sh
   ./rasa_watchdog.sh &
   ```

3. Launch the analytics dashboard:

   ```bash
   cd backend
   streamlit run analytics_dashboard.py --server.headless=true --server.port=8501
   ```

4. Set up monitoring:

   - Access Grafana at [http://your-domain:3001](http://your-domain:3001)
   - Default credentials: admin/admin (change immediately after first login)

### Google Cloud Deployment

1. Authenticate with Google Cloud:

   ```bash
   gcloud auth login
   ```

2. Run the Google Cloud integration script:

   ```bash
   cd backend
   chmod +x gcloud_integration.sh
   ./gcloud_integration.sh
   ```

3. Deploy to Cloud Run:

   ```bash
   gcloud run deploy customer-care-ai \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## 📊 Monitoring and Analytics

The application includes comprehensive monitoring and analytics:

### Real-time Monitoring

- **RASA Watchdog**: Continuous monitoring of service health
- **Prometheus**: Metrics collection for system performance
- **Grafana**: Visualization dashboards for operational metrics
- **Health check endpoints**: Available at `/health`

### Analytics Dashboard

- Advanced analytics for conversation insights
- **Real-time metrics**: User satisfaction, intent distribution, fallback rates
- **Conversation viewer**: Detailed conversation history and analysis
- **Export capabilities**: Download reports in CSV format

### Logging

- **Structured logging**: JSON-formatted logs for easy parsing
- **Log rotation**: Automatic log management
- **Google Cloud Logging**: Integration with cloud-based log analysis
- **Alerting**: Configurable alerts for critical issues







- **Dynamic Data Loading**: Automatically locate and load conversation data from multiple sources
- **Format Detection**: Support for multiple conversation data formats
- **Enhanced Analytics**: Advanced metrics and visualizations
- **Flexible Path Resolution**: Environment variables and fallback paths for reliable data access



1. Configure the data path:

   ```bash
   # In your .env file
   CONVERSATION_DATA_PATH=/path/to/your/conversation/data.json
   ```



   ```bash
   cd backend
   streamlit run analytics_dashboard.py
   ```

3. Access the dashboard at [http://localhost:8501](http://localhost:8501)

4. Use the sidebar filters to analyze specific date ranges or conversation patterns

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on development workflow and coding standards.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [RASA](https://rasa.com/) - The open source machine learning framework for automated text and voice-based conversations

- [Streamlit](https://streamlit.io/) - For the analytics dashboard interface
- [Google Cloud](https://cloud.google.com/) - For cloud deployment and storage solutions
- [](https://.com/) - For the open-source Firebase alternative
- [Docker](https://www.docker.com/) - For containerization

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
-  event logging: All conversation events and feedback are logged (see `/migrations/`)
- Security: RLS enabled on event tables, policies for read/insert


- React 18 + Vite
- Analytics dashboard: `src/Analytics.jsx`
- Feedback modal: `src/Feedback.jsx`
-  Auth: `src/Auth.jsx`
- Code quality: ESLint, Prettier, Vitest

### Scripts & Utilities

- `scripts/generate-secrets.sh`: Generate strong secrets for env
- `scripts/monitor_logs.sh`: Real-time log monitoring
- DB migrations: `/migrations/`

### Configuration

- Environment variables: `.env` (see `.env.example`)
- : Set up project, apply migrations, configure RLS

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
- **Analytics Dashboard**: All dashboard code is now in `dashboard/`. Run with `streamlit run dashboard/dashboard_app.py` for intent distribution, response times, and more.
- **Log Monitoring**: `scripts/monitor_logs.sh` (real-time error/warning tailing)
- **Event Logging**: Conversation and feedback events are stored in (see `/migrations/` for schema and RLS policies)
