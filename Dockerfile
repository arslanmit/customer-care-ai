# syntax=docker/dockerfile:1.4
FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    grep -v '^models/' requirements.txt > /app/requirements-clean.txt && \
    echo "spacy>=3.7.0,<4.0.0" >> /app/requirements-clean.txt && \
    pip install --user -r /app/requirements-clean.txt && \
    apt-get remove -y --auto-remove build-essential curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONPATH=/app/backend \
    PORT=5005 \
    APP_USER=appuser \
    APP_HOME=/home/appuser

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r $APP_USER && \
    useradd -r -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Docker image user" $APP_USER && \
    mkdir -p $APP_HOME && \
    chown -R $APP_USER:$APP_USER $APP_HOME

WORKDIR /app

COPY --from=builder /app/requirements-clean.txt /app/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir rasa==3.5.0 rasa-sdk==3.5.0 && \
    python -m spacy download en_core_web_md && \
    python -m spacy download es_core_news_md && \
    python -m spacy download fr_core_news_md && \
    python -m spacy download de_core_news_md && \
    find /usr/local -type d -name 'test*' -o -name 'tests' -o -name 'idle_test' | xargs rm -rf 2>/dev/null || true && \
    find /usr/local -type f -name '*.pyc' -o -name '*.pyo' | xargs rm -f 2>/dev/null || true && \
    rm -f /app/requirements-clean.txt

ENV PYTHONPATH=/app

COPY --chown=$APP_USER:$APP_USER backend/ ./backend/
COPY --chown=$APP_USER:$APP_USER run.py .

RUN chown -R $APP_USER:$APP_USER /app

USER $APP_USER

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

EXPOSE $PORT

LABEL maintainer="arslanmit@gmail.com" \
      org.opencontainers.image.source="https://github.com/arslanmit/customer-care-ai"

CMD ["python", "-m", "rasa", "run", "--enable-api", "--cors", "*", "--debug", "--port", "${PORT}"]