# Use Python 3.10 slim base image for builder stage
FROM python:3.10-slim as builder

# Set environment variables
ENV \
    # Python
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    # Pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-dev --no-root --no-ansi \
    && poetry export --without-hashes --format=requirements.txt > requirements.txt \
    # Clean up build dependencies
    && apt-get remove -y --auto-remove build-essential curl git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Runtime stage
FROM python:3.10-slim

# Set environment variables
ENV \
    # Python
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    # Pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # App
    PYTHONPATH=/app/backend \
    PORT=5005 \
    # Non-root user
    APP_USER=appuser \
    APP_HOME=/home/appuser

# Create non-root user and set up directory
RUN set -ex \
    && groupadd -r $APP_USER \
    && useradd -r -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Docker image user" $APP_USER \
    && mkdir -p $APP_HOME \
    && chown -R $APP_USER:$APP_USER $APP_HOME

# Set working directory
WORKDIR /app

# Install system dependencies
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install Python dependencies
RUN set -ex \
    && pip install --no-cache-dir -r requirements.txt \
    && find /usr/local -depth \\( \\( -type d -a \\( -name test -o -name tests -o -name idle_test \\) \\) \
                    -o \\( -type f -a \\( -name '*.pyc' -o -name '*.pyo' \\) \\) \\) -exec rm -rf '{}' +

# Copy application code
COPY --chown=$APP_USER:$APP_USER backend/ ./backend/
COPY --chown=$APP_USER:$APP_USER run.py .

# Set file permissions
RUN chown -R $APP_USER:$APP_USER /app

# Switch to non-root user
USER $APP_USER

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Expose the port the app runs on
EXPOSE $PORT

# Set labels
LABEL maintainer="arslanmit@gmail.com"
LABEL org.opencontainers.image.source="https://github.com/arslanmit/customer-care-ai"

# Command to run the application
CMD ["python", "-m", "rasa", "run", "--enable-api", "--cors", "*", "--debug", "--port", "${PORT}"]
