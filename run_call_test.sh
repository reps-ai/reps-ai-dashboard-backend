#!/bin/bash
# Script to test the trigger_call functionality with Retell integration

# Set up error handling
set -e
echo "🚀 Starting trigger_call test..."

# Load environment variables from .env if available
if [ -f .env ]; then
  echo "🔄 Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️  Warning: No .env file found. Make sure environment variables are set."
  echo "Required: RETELL_API_KEY, RETELL_FROM_NUMBER, DATABASE_URL"
  exit 1
fi

# Verify essential environment variables
if [ -z "$RETELL_API_KEY" ]; then
  echo "❌ RETELL_API_KEY not set. Please add it to your .env file."
  exit 1
fi

if [ -z "$RETELL_FROM_NUMBER" ]; then
  echo "❌ RETELL_FROM_NUMBER not set. Please add it to your .env file."
  exit 1
fi

# Check if Celery worker is running
celery_running=$(ps aux | grep "celery worker" | grep -v grep | wc -l)

if [ "$celery_running" -eq 0 ]; then
  echo "🌱 Starting Celery worker..."
  # Start celery in background
  celery -A backend.celery_app worker -l INFO -E -Q call_tasks &
  # Store PID
  CELERY_PID=$!
  # Wait for Celery worker to start
  echo "⏳ Waiting for Celery worker to start..."
  sleep 5
  echo "✅ Celery worker started with PID: $CELERY_PID"
else
  echo "✅ Celery worker is already running"
fi

# Run the test script
echo "🔄 Triggering test call..."
python test_trigger_call_integration.py

# Check if we started Celery and need to stop it
if [ -n "$CELERY_PID" ]; then
  echo "🛑 Stopping Celery worker..."
  kill $CELERY_PID
  # Give it time to shut down
  sleep 2
  echo "✅ Celery worker stopped"
fi

echo "✅ Test completed successfully" 