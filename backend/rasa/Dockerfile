FROM rasa/rasa:3.6.20-full

# Switch to root to install dependencies
USER root

# Copy requirements file
COPY requirements-rasa.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-rasa.txt

# Switch back to the default user
USER 1001
