FROM rasa/rasa-sdk:3.12.1

# Switch to root to install dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better caching
COPY requirements-actions.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-actions.txt

# Switch back to non-root user
USER 1001

# Copy actions code
COPY . /app/actions/

# Set the working directory
WORKDIR /app

# Use the same command as before
CMD ["start", "--actions", "actions.actions"]
