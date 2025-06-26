# syntax=docker/dockerfile:1.4

# Use a single stage for simplicity and reliability
FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install all necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Set up a non-root user for security
ENV APP_USER=appuser \
    APP_HOME=/home/appuser
RUN groupadd -r $APP_USER && \
    useradd -r -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Docker image user" $APP_USER
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for the application
ENV PYTHONPATH=/app/backend \
    PORT=5005 \
    RASA_ENVIRONMENT=production \
    RASA_ACTIONS_URL=http://localhost:5055/webhook

# Copy application code
COPY --chown=$APP_USER:$APP_USER backend/ ./backend/
COPY --chown=$APP_USER:$APP_USER scripts/entrypoint.sh /usr/local/bin/entrypoint.sh

# Set ownership and user
RUN chown -R $APP_USER:$APP_USER /app
USER $APP_USER

# Expose port and set health check
EXPOSE $PORT
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Metadata and entrypoint
LABEL maintainer="arslanmit@gmail.com" \
      org.opencontainers.image.source="https://github.com/arslanmit/customer-care-ai"
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]