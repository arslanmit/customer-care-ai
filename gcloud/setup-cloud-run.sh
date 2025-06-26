#!/bin/bash
set -e

# Get the current project ID
PROJECT_ID=$(gcloud config get-value project)
REGION="europe-west1"
SERVICE_NAME="customer-care-ai"
SERVICE_ACCOUNT="customer-care-ai@${PROJECT_ID}.iam.gserviceaccount.com"

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com

# Create a service account for the application
echo "Creating service account ${SERVICE_ACCOUNT}..."
gcloud iam service-accounts create ${SERVICE_NAME} \
  --display-name "Customer Care AI Service Account" \
  --project=${PROJECT_ID} || echo "Service account may already exist"

# Add IAM bindings for the service account
echo "Adding IAM bindings..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudsql.client" \
  --project=${PROJECT_ID} || true

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" \
  --project=${PROJECT_ID} || true

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/logging.logWriter" \
  --project=${PROJECT_ID} || true

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/monitoring.metricWriter" \
  --project=${PROJECT_ID} || true



# Create a Cloud SQL instance (uncomment if needed)
echo "Creating Cloud SQL instance..."
gcloud sql instances create customer-care-ai-db \
  --database-version=POSTGRES_13 \
  --cpu=1 \
  --memory=3840MB \
  --region=${REGION} \
  --project=${PROJECT_ID} || echo "Cloud SQL instance may already exist"

# Create a database
echo "Creating database..."
gcloud sql databases create customer_care_ai \
  --instance=customer-care-ai-db \
  --project=${PROJECT_ID} || echo "Database may already exist"

# Update the root password (uncomment and set a secure password)
# gcloud sql users set-password postgres \
#   --instance=customer-care-ai-db \
#   --password=YOUR_SECURE_PASSWORD \
#   --project=${PROJECT_ID}

echo "Setup complete!"
echo "Next steps:"
echo "1. Update the DATABASE_URL in the Cloud Run service with the connection string"
echo "2. Trigger a new build with: gcloud builds submit --config=cloudbuild.yaml --async ."
echo "3. Monitor the build in the Cloud Console: https://console.cloud.google.com/cloud-build"
