# Dockerfile for Rasa backend
FROM rasa/rasa:3.6.0-full

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install additional Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Make sure the entrypoint script has execute permissions
RUN chmod +x /app/entrypoint.sh || true

# Expose Rasa and action server ports
EXPOSE 5005 5055

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
