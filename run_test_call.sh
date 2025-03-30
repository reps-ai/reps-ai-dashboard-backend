#!/bin/bash
# Script to test the Retell integration and call handling

# Set up error handling
set -e
echo "🚀 Starting test call flow..."

# Check if Python environment is active
if [ -z "$VIRTUAL_ENV" ]; then
  echo "⚠️  Warning: No Python virtual environment detected. Consider activating one."
fi

# Load environment variables from .env if available
if [ -f .env ]; then
  echo "🔄 Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️  Warning: No .env file found. Make sure environment variables are set."
fi

# Check if Celery worker is running
celery_running=$(ps aux | grep "celery worker" | grep -v grep | wc -l)

if [ "$celery_running" -eq 0 ]; then
  echo "🌱 Starting Celery worker..."
  # Start celery in background
  celery -A backend.celery_app worker -l INFO -E -Q call_tasks &
  # Store PID
  CELERY_PID=$!
  # Wait for Celery to start
  echo "⏳ Waiting for Celery worker to start..."
  sleep 5
  echo "✅ Celery worker started with PID: $CELERY_PID"
else
  echo "✅ Celery worker is already running"
fi

# Run the test script
echo "🔄 Triggering test call..."
python test_trigger_call.py

# Check if we started Celery and need to stop it
if [ -n "$CELERY_PID" ]; then
  echo "🛑 Stopping Celery worker..."
  kill $CELERY_PID
  # Give it time to shut down
  sleep 2
  echo "✅ Celery worker stopped"
fi

echo "✅ Test completed successfully"
