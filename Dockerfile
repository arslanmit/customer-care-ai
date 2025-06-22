# Dockerfile for Rasa backend
FROM rasa/rasa:3.6.0-full

# Set working directory
WORKDIR /app

# Copy only necessary files first to leverage Docker cache
COPY requirements.txt ./

COPY entrypoint.sh /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Install additional Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Rasa and action server ports
EXPOSE 5005 5055

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
