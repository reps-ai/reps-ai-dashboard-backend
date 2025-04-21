#!/bin/bash

# Exit on any error
set -e

echo "🔄 Pulling latest changes from main branch..."
git pull origin main

echo "🛑 Stopping existing Docker containers..."
docker-compose down

echo "🧹 Cleaning up Docker images..."
# Remove any dangling images
docker system prune -f

echo "🏗️ Building fresh Docker containers..."
docker-compose build --no-cache

echo "🚀 Starting Docker containers..."
docker-compose up -d

echo "✅ Deployment complete! Container is now running with latest changes."

# Print the container status
docker-compose ps 