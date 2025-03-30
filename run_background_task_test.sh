#!/bin/bash

# Script to test the Celery background task for trigger_call

# Colors for better output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}===== Testing Trigger Call with Celery Background Task =====${NC}"

# Step 1: Make sure Celery worker is running
echo -e "${YELLOW}Step 1: Checking if Celery worker is running...${NC}"
if pgrep -f "celery -A backend.celery_app worker" > /dev/null
then
    echo -e "${GREEN}Celery worker is already running.${NC}"
else
    echo -e "${RED}Celery worker is not running. Starting it now...${NC}"
    # Start Celery worker in the background
    celery -A backend.celery_app worker --loglevel=info --concurrency=4 -Q call_tasks &
    # Wait for worker to start
    sleep 5
    echo -e "${GREEN}Celery worker started.${NC}"
fi

# Step 2: Run the test script
echo -e "${YELLOW}Step 2: Running test_trigger_call_integration.py...${NC}"
python test_trigger_call_integration.py

# Step 3: Check Celery logs
echo -e "${YELLOW}Step 3: Monitoring Celery logs for task execution (press Ctrl+C to stop)...${NC}"
echo -e "${GREEN}Waiting for the background task to execute...${NC}"
echo -e "${BLUE}Look for 'Creating Retell call for database call ID' in the logs${NC}"

# Attach to Celery logs
if pgrep -f "celery -A backend.celery_app worker" > /dev/null
then
    # Use tail to follow the Celery logs - user can Ctrl+C to exit
    tail -f celery.log 2>/dev/null || echo -e "${RED}Could not find celery.log${NC}"
else
    echo -e "${RED}Celery worker is not running, cannot monitor logs.${NC}"
fi

echo -e "${BLUE}===== Test Complete =====${NC}"
echo -e "${GREEN}Note: To see the full process, check the database for the call record and verify that:${NC}"
echo -e "${GREEN}1. The initial call has status 'scheduled'${NC}"
echo -e "${GREEN}2. After the background task runs, it should have an external_call_id and updated status${NC}" 