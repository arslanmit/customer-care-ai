FROM node:16-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies including node-fetch
RUN npm install --production

# Copy all files
COPY . .

# Expose the port
EXPOSE 8080

# Start the server
CMD ["node", "server.js"]
