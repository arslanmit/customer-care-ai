# Use the official Rasa SDK image as a base
FROM rasa/rasa-sdk:3.12.1

# Set the working directory
WORKDIR /app

# Copy the requirements file from the root of the context
COPY requirements.txt .

# Switch to root to install dependencies
USER root

# Install Python dependencies, excluding rasa and rasa-sdk
RUN grep -vE '^rasa==|^rasa-sdk==' requirements.txt > actions-requirements.txt && \
    pip install --no-cache-dir -r actions-requirements.txt

# Copy the actions code into the container
COPY backend/rasa/actions/ /app/actions/

# Change ownership of the app directory back to the default user (UID 1001)
RUN chown -R 1001:0 /app

# Switch back to the default non-root user
USER 1001
