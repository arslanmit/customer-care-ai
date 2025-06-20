#!/bin/bash

# Generate secure random secrets
generate_secret() {
    LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*()_+-=[]{}|;:,.<>?' < /dev/urandom | head -c 64
}

generate_rsa_key() {
    openssl genrsa 4096 2>/dev/null | head -n -1 | tail -n +2 | tr -d '\n'
}

# Generate secrets
RASA_JWT_SECRET=$(generate_secret)
RASA_JWT_PRIVATE_KEY=$(generate_rsa_key)
POSTGRES_PASSWORD=$(generate_secret)
REDIS_PASSWORD=$(generate_secret)
JWT_SECRET=$(generate_secret)
SESSION_SECRET=$(generate_secret)
CSRF_SECRET=$(generate_secret)

# Update .env file
sed -i '' -e "s|RASA_JWT_SECRET=.*|RASA_JWT_SECRET=$RASA_JWT_SECRET|" \
         -e "s|RASA_JWT_PRIVATE_KEY=.*|RASA_JWT_PRIVATE_KEY='$RASA_JWT_PRIVATE_KEY'|" \
         -e "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD='$POSTGRES_PASSWORD'|" \
         -e "s|REDIS_PASSWORD=.*|REDIS_PASSWORD='$REDIS_PASSWORD'|" \
         -e "s|JWT_SECRET=.*|JWT_SECRET='$JWT_SECRET'|" \
         -e "s|SESSION_SECRET=.*|SESSION_SECRET='$SESSION_SECRET'|" \
         -e "s|CSRF_SECRET=.*|CSRF_SECRET='$CSRF_SECRET'|" \
         .env

echo "Secrets have been generated and updated in the .env file"
