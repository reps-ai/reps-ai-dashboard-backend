#!/usr/bin/env bash
set -e

# Function to log messages with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Change to script directory (project root)
cd "$(dirname "$0")"

# Build the Docker image with a tag
log "Building Docker image 'reps-ai-backend:latest'..."
if ! docker build -t reps-ai-backend:latest .; then
    log "[ERROR] Failed to build Docker image"
    exit 1
fi

# Stop and remove any existing container
log "Stopping and removing old container if it exists..."
docker rm -f reps-ai-backend 2>/dev/null || true

# Run the Docker container in detached mode
log "Starting new container 'reps-ai-backend'..."
if ! docker run -d \
    --name reps-ai-backend \
    -p 8000:8000 \
    -p 6379:6379 \
    --restart unless-stopped \
    reps-ai-backend:latest; then
    log "[ERROR] Failed to start container"
    exit 1
fi

# Wait for container to be healthy
log "Waiting for application to be ready..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        log "[SUCCESS] Application is up and running!"
        log "API is available at: http://localhost:8000"
        log "Redis is available at: localhost:6379"
        log "View logs with: docker logs -f reps-ai-backend"
        exit 0
    fi
    log "Waiting for application to become ready... (attempt $i/10)"
    sleep 3
done

# If we get here, the health check failed
log "[ERROR] Application failed to become healthy after 30 seconds"
log "Container logs:"
docker logs reps-ai-backend
docker rm -f reps-ai-backend
exit 1 