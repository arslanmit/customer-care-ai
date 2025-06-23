# Contributing to Customer Care AI

Thank you for your interest in contributing to our project! This guide will help you get started with the development environment and contribution workflow.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)

## Prerequisites

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- Git

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/customer-care-ai.git
   cd customer-care-ai
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## Running the Application

### Backend Services
```bash
docker-compose up -d  # Start database and monitoring
python -m rasa run --cors "*" --debug  # Run Rasa server
python -m rasa run actions  # Run Rasa actions server
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test/unit/backend/test_actions.py

# Run with coverage
pytest --cov=backend test/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Code Style

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function signatures
- Keep functions small and focused
- Document public APIs with docstrings

### JavaScript/TypeScript
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ES6+ features
- Prefer functional programming patterns

## Pull Request Process

1. Fork the repository and create your branch from `main`
2. Make your changes
3. Add tests for new features
4. Update documentation as needed
5. Ensure all tests pass
6. Submit a pull request

## Code Review Guidelines

- Keep PRs focused and small
- Include clear descriptions of changes
- Reference related issues
- Request reviews from relevant team members

## License

By contributing, you agree that your contributions will be licensed under the project's license.
