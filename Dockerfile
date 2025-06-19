# Dockerfile for Rasa backend
FROM rasa/rasa:3.6.0-full

# Set working directory
WORKDIR /app

# Copy all project files into the image
COPY . /app

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose Rasa and action server ports
EXPOSE 5005 5055

ENTRYPOINT ["/app/entrypoint.sh"]
