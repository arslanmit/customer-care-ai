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
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Create a temporary requirements file without the model files
RUN set -ex \
    && grep -v '^models/' requirements.txt > /app/requirements-clean.txt \
    && echo "spacy>=3.7.0,<4.0.0" >> /app/requirements-clean.txt

# Install Python dependencies
RUN set -ex \
    && pip install --user -r /app/requirements-clean.txt \
    # Clean up build dependencies
    && apt-get remove -y --auto-remove build-essential curl git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

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

# Copy the cleaned requirements file from the builder stage
COPY --from=builder /app/requirements-clean.txt /app/requirements.txt

# Install Python dependencies
RUN set -ex \
    && pip install --no-cache-dir -r /app/requirements.txt \
    # Install spaCy models
    && python -m spacy download en_core_web_md \
    && python -m spacy download es_core_news_md \
    && python -m spacy download fr_core_news_md \
    && python -m spacy download de_core_news_md \
    # Clean up
    && find /usr/local -type d -name 'test*' -o -name 'tests' -o -name 'idle_test' | xargs rm -rf 2>/dev/null || true \
    && find /usr/local -type f -name '*.pyc' -o -name '*.pyo' | xargs rm -f 2>/dev/null || true \
    && rm -f /app/requirements-clean.txt

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
