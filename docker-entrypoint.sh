#!/bin/bash
set -e

# Start Redis server in the background
redis-server --daemonize yes

# Wait for Redis to be ready
until redis-cli ping; do
  echo "Waiting for Redis to be ready..."
  sleep 1
done

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload 