# syntax=docker/dockerfile:1.4
FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN grep -v '^models/' requirements.txt > /app/requirements-clean.txt && \
    pip install --user -r /app/requirements-clean.txt && \
    apt-get remove -y --auto-remove build-essential curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

FROM python:3.10-slim

# Cloud Run requires the PORT environment variable to be set to 8080
# but we'll make it configurable for local development
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONPATH=/app/backend \
    # Default to 5005 for local development, overridden by Cloud Run to 8080
    PORT=5005 \
    # RASA environment variables
    RASA_ENVIRONMENT=production \
    RASA_ACTIONS_URL=http://localhost:5055/webhook \
    # Application settings
    APP_USER=appuser \
    APP_HOME=/home/appuser

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r $APP_USER && \
    useradd -r -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Docker image user" $APP_USER && \
    mkdir -p $APP_HOME && \
    chown -R $APP_USER:$APP_USER $APP_HOME

WORKDIR /app

COPY --from=builder /app/requirements-clean.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt && \
    find /usr/local -type d -name 'test*' -o -name 'tests' -o -name 'idle_test' | xargs rm -rf 2>/dev/null || true && \
    find /usr/local -type f -name '*.pyc' -o -name '*.pyo' | xargs rm -f 2>/dev/null || true && \
    rm -f /app/requirements-clean.txt

ENV PYTHONPATH=/app

COPY --chown=$APP_USER:$APP_USER backend/ ./backend/
COPY --chown=$APP_USER:$APP_USER scripts/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chown -R $APP_USER:$APP_USER /app

USER $APP_USER

# Health check for Cloud Run
# Note: Cloud Run has its own health checking, but we'll keep this for local development
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

EXPOSE $PORT

LABEL maintainer="arslanmit@gmail.com" \
      org.opencontainers.image.source="https://github.com/arslanmit/customer-care-ai"

# Start Rasa using the entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]