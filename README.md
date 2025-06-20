# Customer Care AI Chatbot

A full-stack conversational AI chatbot built with Rasa (backend) and React (frontend), designed to handle customer service inquiries with multilingual support and advanced conversation management.

## 🚀 Key Features

- **Multilingual Support**: English, Spanish, French, German, and Turkish
- **Advanced Conversation Flow**: Stateful conversations with context management
- **Production-Ready**: Containerized with Docker and Kubernetes support
- **Enterprise-Grade Security**: Secure by default with industry best practices
- **Scalable Architecture**: Microservices-based design with Redis for caching
- **Monitoring**: Integrated with Prometheus and Grafana
- **CI/CD**: Automated testing and deployment with GitHub Actions

## 🏗️ Project Structure

```text
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
│   └── generate-secrets.sh # Secure secret generation
├── .env.example         # Environment variables template
├── docker-compose.yml    # Local development
├── docker-compose.prod.yml # Production deployment
├── Dockerfile.rasa       # Rasa production Dockerfile
├── Dockerfile.actions    # Actions server Dockerfile
├── requirements.txt     # Python dependencies
└── setup.sh            # Setup script
```

## 🛠️ Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Redis 6.0+
- PostgreSQL 13+
- OpenSSL (for certificate generation)
- jq (for JSON processing in scripts)

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

## 🔒 Security Best Practices

### 🔐 Security Features

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

### 🛡️ Security Controls

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

### 🚨 Incident Response

- **Monitoring**:
  - Real-time security monitoring
  - Anomaly detection
  - Automated alerts

- **Response**:
  - Incident response plan
  - Automated remediation
  - Forensic capabilities

### 📝 Security Documentation

- [Security Policy](SECURITY.md)
- [Incident Response Plan](docs/INCIDENT_RESPONSE.md)
- [Compliance Documentation](docs/COMPLIANCE.md)

### 🔄 Security Updates

- Regular dependency updates
- Security patch management
- CVE monitoring and response

## 🛠️ Development Security

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Security Scanning

```bash
# Run security scans
./scripts/security-scan.sh
```

### Dependency Auditing

```bash
# Check for vulnerable dependencies
npm audit
pip-audit
```

## 🔍 Security Monitoring

### Logging

- Structured logging with security context
- Centralized log management
- Long-term log retention

### Alerting

- Real-time security alerts
- Escalation policies
- On-call rotations

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

---

> **Note**: This application includes security features that should be configured according to your organization's security policies and compliance requirements. Always consult with your security team before deploying to production.

### 1. Secure Configuration

- **Secrets Management**:
  - All secrets are stored in `.env` (never committed to version control)
  - Use the provided `scripts/generate-secrets.sh` to generate strong secrets
  - Consider using a secrets manager in production (e.g., AWS Secrets Manager, HashiCorp Vault)

- **Docker Security**:
  - Containers run as non-root users
  - Read-only filesystems where possible
  - Minimal base images
  - Regular security scanning of container images

### 2. Network Security

- **TLS/SSL**:
  - Enable HTTPS with valid certificates (use Let's Encrypt in production)
  - Configure HSTS headers
  - Enable TLS 1.2+ only

- **Firewall Rules**:
  - Restrict access to management interfaces
  - Use VPC peering for internal communication
  - Implement network policies in Kubernetes

### 3. Authentication & Authorization

- **JWT Authentication**:
  - Secure token storage
  - Short-lived access tokens
  - Secure cookie settings

- **Rate Limiting**:
  - Implemented at the API gateway level
  - Configurable rate limits per endpoint

### 4. Monitoring & Logging

- **Security Monitoring**:
  - Log all authentication attempts
  - Monitor for suspicious activities
  - Set up alerts for security events

- **Audit Logs**:
  - Log all administrative actions
  - Centralized log management
  - Long-term storage with rotation

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
