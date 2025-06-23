# Use Python 3.10 slim base image for builder stage
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies
RUN poetry install --no-dev --no-root && \
    # Clean up build dependencies
    apt-get remove -y --auto-remove build-essential curl git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Runtime stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install additional Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/
COPY run.py .

# Switch to a non-root user
USER 1001

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PORT=5005

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the Rasa server
CMD ["python", "-m", "rasa", "run", "--enable-api", "--cors", "*", "--debug", "--port", "$PORT"]
