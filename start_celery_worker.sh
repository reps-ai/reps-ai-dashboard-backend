#!/bin/bash
# Script to start Celery worker

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Check if we should use a specific queue
QUEUE=${1:-"default"}
CONCURRENCY=${2:-4}
LOGLEVEL=${3:-"INFO"}

# Verify Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "Redis server not found. Please install Redis first:"
    echo "  macOS: brew install redis"
    echo "  Ubuntu/Debian: sudo apt install redis-server"
    echo "  Or use a Docker container: docker run -d -p 6379:6379 redis:7"
    exit 1
fi

# Check if Redis is already running
if ! redis-cli ping &> /dev/null; then
    echo "Redis is not running. Starting Redis server..."
    
    # Check if this is a macOS system using brew
    if command -v brew &> /dev/null && [ -d "$(brew --prefix)/etc/redis" ]; then
        brew services start redis
        echo "Started Redis using Homebrew services"
    # Otherwise try to start the server directly
    else
        redis-server --daemonize yes
        sleep 1
        
        if ! redis-cli ping &> /dev/null; then
            echo "Failed to start Redis. Please start it manually or verify installation."
            exit 1
        fi
        echo "Started Redis server in background"
    fi
else
    echo "Redis is already running"
fi

# Start the worker
echo "Starting Celery worker for queue: $QUEUE with concurrency: $CONCURRENCY"
celery -A backend.celery_app worker -Q $QUEUE -c $CONCURRENCY --loglevel=$LOGLEVEL 