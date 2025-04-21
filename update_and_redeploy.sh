#!/bin/bash

# Exit on any error
set -e

# Change to the repository directory (adjust this path to your repo location)
REPO_DIR="/Users/home/reps-ai-backend/reps-ai-dashboard-backend"
cd "$REPO_DIR"
echo "📂 Changed to repository directory: $(pwd)"

# Update the repository (ensuring we're in the repo directory)
echo "🔄 Pulling latest changes from main branch..."
git pull origin main

# Print working directory for debugging
echo "📂 Current directory: $(pwd)"

# Configure Docker for non-interactive use
echo "🔧 Configuring Docker for non-interactive use..."
export DOCKER_CLI_EXPERIMENTAL=enabled
export DOCKER_SCAN_SUGGEST=false
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Setup Docker credential helper (if it exists)
if [ -f "$REPO_DIR/docker-credential-helper.sh" ]; then
  chmod +x "$REPO_DIR/docker-credential-helper.sh"
  export DOCKER_CONFIG="$HOME/.docker"
  mkdir -p "$DOCKER_CONFIG"
  echo '{"credsStore":""}' > "$DOCKER_CONFIG/config.json"
  echo '{"auths":{"https://index.docker.io/v1/":{}}}' > "$DOCKER_CONFIG/config.json"
  echo "✅ Configured Docker credential helper"
fi

echo "🛑 Stopping existing Docker containers..."
docker-compose down || true

echo "🧹 Cleaning up Docker images..."
# Remove any dangling images
docker system prune -f || true

echo "🏗️ Building fresh Docker containers..."
# Using --no-cache to force fresh build but allowing image pull to fail gracefully
docker-compose build --no-cache || docker-compose build

echo "🚀 Starting Docker containers..."
docker-compose up -d

echo "✅ Deployment complete! Container is now running with latest changes."

# Print the container status
docker-compose ps 