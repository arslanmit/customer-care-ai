.PHONY: install test lint format check-style clean help

# Variables
PYTHON = python3
PIP = pip3
PYTEST = python -m pytest
COVERAGE = python -m coverage
BLACK = black
ISORT = isort
FLAKE8 = flake8
MYPY = mypy

# Default target
help:
	@echo "\nAvailable targets:"
	@echo "  install        Install development dependencies (requirements.txt, requirements-test.txt, pre-commit)"
	@echo "  test           Run all tests with coverage report"
	@echo "  test-fast      Run tests without coverage (faster)"
	@echo "  lint           Run all Python linters (mypy, black, isort, flake8)"
	@echo "  format         Format code with black and isort"
	@echo "  check-style    Check code style without making changes"
	@echo "  clean          Remove Python cache, build, and test artifacts"
	@echo "  run            Run the Rasa server"
	@echo "  actions        Run the Rasa actions server"
	@echo "  docker-up      Start all services with Docker Compose"
	@echo "  docker-down    Stop and remove all Docker Compose services"
	@echo "  docker-logs    View logs from Docker Compose services"
	@echo "  pre-commit-all Run pre-commit on all files"
	@echo "\nFor script utilities, see: scripts/help.sh\n"
	@echo "  rasa-validate Validate all Rasa data using modular YAMLs"
	@echo "  rasa-train    Train Rasa model using modular YAMLs"
	@echo "  clean       Remove build artifacts and caches"
	@echo "  help        Show this help message"

# Install dependencies
install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-test.txt
	$(PIP) install -e .
	pre-commit install

# Run tests with coverage
test:
	$(PYTEST) --cov=backend --cov-report=html --cov-report=term-missing test/

# Run tests without coverage
test-fast:
	$(PYTEST) -v test/

# Run all linters
lint: check-style
	$(MYPY) backend/

# Format code
format:
	$(BLACK) backend/
	$(ISORT) backend/
# Check code style without making changes
check-style:
	$(BLACK) --check backend/
	$(ISORT) --check-only backend/
	$(FLAKE8) backend/
# Clean up
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	find . -type d -name '.coverage' -delete
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name '.hypothesis' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	find . -type f -name '*.so' -delete
	find . -type f -name '*.c' -delete
	find . -type f -name '*.o' -delete
	find . -type f -name '*~' -delete
	find . -type f -name '*.swp' -delete
	find . -type f -name '*.swo' -delete

# Run the application
run:
	python -m rasa run --cors "*" --debug

# Run actions server
actions:
	python -m rasa run actions --debug

# Run the full stack with docker
docker-up:
	docker-compose up -d --build

# Stop and remove docker containers
docker-down:
	docker-compose down

# View logs
docker-logs:
	docker-compose logs -f

# Run pre-commit on all files
pre-commit-all:
	pre-commit run --all-files
