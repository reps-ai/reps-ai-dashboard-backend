"""
Test script for the process_retell_call task.
"""
import asyncio
import json
import uuid
from datetime import datetime

# Import necessary modules
from backend.db.connections.database import SessionLocal
from backend.db.models.call.call_log import CallLog
from backend.tasks.call.task_definitions import process_retell_call

# Function to create a test call in the database
async def create_test_call():
    """Create a test call record in the database."""
    db = SessionLocal()
    try:
        # Create a new call record with all UUIDs
        test_call_id = str(uuid.uuid4())
        lead_id = str(uuid.uuid4())  # Proper UUID for lead_id
        
        new_call = CallLog(
            id=test_call_id,
            lead_id=lead_id,
            call_status="scheduled"
        )
        
        # Add to database
        db.add(new_call)
        await db.commit()
        
        print(f"Created test call with ID: {test_call_id}")
        print(f"Test call has lead ID: {lead_id}")
        return test_call_id
    except Exception as e:
        await db.rollback()
        print(f"Error creating test call: {str(e)}")
        raise
    finally:
        await db.close()

# Run the async function to create a test call
loop = asyncio.get_event_loop()
test_call_id = loop.run_until_complete(create_test_call())

# Create a mock Retell response similar to what would be returned by the API
mock_retell_data = {
    "call_id": "test_call_" + str(uuid.uuid4())[0:8],
    "call_status": "registered",
    "start_timestamp": int(datetime.now().timestamp() * 1000),
    "end_timestamp": int(datetime.now().timestamp() * 1000) + 60000,  # 1 minute later
    "recording_url": "https://example.com/recording.wav",
    "transcript": "This is a test transcript for the call",
    "call_analysis": {
        "call_summary": "This was a test call summary",
        "user_sentiment": "Positive"
    },
    "metadata": {
        "lead_id": "test_lead_" + str(uuid.uuid4())[0:8],
        "campaign_id": "test_campaign_" + str(uuid.uuid4())[0:8]
    }
}

print(f"Starting test with call ID: {test_call_id}")
print(f"Mock Retell data: {json.dumps(mock_retell_data, indent=2)}")

# Call the task synchronously (this will not go through Celery)
# This is for testing the task function works at all
try:
    print("\nTesting synchronous function execution:")
    result = process_retell_call(test_call_id, mock_retell_data)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {str(e)}")

# Now let's submit as an actual Celery task
from backend.celery_app import app
print("\nSubmitting as Celery task:")
task = app.send_task(
    'call.process_retell_call',
    args=[test_call_id, mock_retell_data],
    queue='call_tasks'
)
print(f"Task ID: {task.id}")
print("Check the worker logs to see if the task is processed") 