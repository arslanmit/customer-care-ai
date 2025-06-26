# Use the official Rasa SDK image as a base
FROM rasa/rasa-sdk:3.6.2

# Set the working directory
WORKDIR /app

# Switch to root to install dependencies and set permissions
USER root

# Copy the dedicated actions requirements file
COPY requirements-actions.txt .

# Install the Python dependencies for the actions
RUN pip install --no-cache-dir -r requirements-actions.txt

# Copy the actions code into the container
COPY . /app/actions/

# Change ownership of the app directory back to the default user (UID 1001)
RUN chown -R 1001:0 /app

# Switch back to the default non-root user
USER 1001
