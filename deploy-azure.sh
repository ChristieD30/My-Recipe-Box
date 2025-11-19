#!/bin/bash

# Azure deployment script for Recipe Box
set -e

echo "🚀 Starting Azure deployment..."

# Variables
RESOURCE_GROUP="recipe-box-rg"
LOCATION="Central US"
CONTAINER_NAME="recipe-box-app"
DNS_LABEL="recipe-box-christie"

# 1. Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# 2. Build and tag image for Docker Hub
echo "🏗️  Building and tagging image..."
docker build -t recipe-box .
docker tag recipe-box $DOCKER_USERNAME/recipe-box:latest

# 3. Push to Docker Hub (you need to set DOCKER_USERNAME)
echo "⬆️  Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/recipe-box:latest

# 4. Deploy to Azure Container Instances
echo "☁️  Deploying to Azure..."
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $DOCKER_USERNAME/recipe-box:latest \
  --dns-name-label $DNS_LABEL \
  --ports 5000 \
  --environment-variables \
    SECRET_KEY="$(openssl rand -base64 32)" \
    FLASK_ENV="production" \
  --cpu 1 \
  --memory 1.5 \
  --restart-policy Always

# 5. Get the URL
echo "🌐 Getting app URL..."
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --query "{URL:ipAddress.fqdn,State:instanceView.state}" \
  --out table

echo "✅ Deployment complete!"
echo "Your app will be available at: http://$DNS_LABEL.$LOCATION.azurecontainer.io:5000"