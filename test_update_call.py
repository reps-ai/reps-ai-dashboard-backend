"""
Test script to update a specified call ID with mock Retell data.
"""
import json
from datetime import datetime, timedelta
import time

# The call ID provided by the user
CALL_ID = "350b148b-6e7c-444d-abef-6cec1f6f477a"

# Create mock Retell data with realistic values
now = datetime.now()
start_time = int(now.timestamp() * 1000)
end_time = int((now + timedelta(minutes=2)).timestamp() * 1000)

mock_retell_data = {
    "call_id": "retell_" + CALL_ID[:8],
    "call_status": "registered",
    "start_timestamp": start_time,
    "end_timestamp": end_time,
    "recording_url": "https://storage.retell.ai/recordings/" + CALL_ID + ".wav",
    "transcript": "Agent: Hello, this is Reps AI calling about your recent interest in our gym membership. How are you today?\nUser: I'm doing well, thanks for calling.\nAgent: Great! I wanted to follow up on your inquiry about membership options. What kind of fitness program are you interested in?\nUser: I'm looking for something with group classes, especially HIIT workouts.\nAgent: Perfect! We have several HIIT classes throughout the week. Would you like to schedule a time to visit the gym for a tour and a free class?\nUser: Yes, that sounds good.\nAgent: Wonderful! How about this Thursday at 6pm?\nUser: Thursday works for me, see you then!\nAgent: Excellent! I've booked your appointment for Thursday at 6pm. Looking forward to seeing you then!",
    "call_analysis": {
        "call_summary": "The lead was interested in HIIT workout classes. Successfully scheduled a gym tour and free class for Thursday at 6pm.",
        "user_sentiment": "Positive",
        "call_successful": True
    },
    "metadata": {
        "lead_id": CALL_ID,
        "campaign_id": "9427e0d4-bede-479c-a07a-2078592c6cd5"
    }
}

print(f"Updating call ID: {CALL_ID}")
print(f"Mock Retell data: {json.dumps(mock_retell_data, indent=2)}")

# Import the task directly and run it synchronously (not through Celery)
from backend.tasks.call.task_definitions import process_retell_call

print("\nRunning the task synchronously:")
result = process_retell_call(CALL_ID, mock_retell_data)
print(f"Result: {result}")

# Alternatively, submit as a Celery task
from backend.celery_app import app

print("\nSubmitting as a Celery task:")
task = app.send_task(
    'call.process_retell_call',
    args=[CALL_ID, mock_retell_data],
    queue='call_tasks'
)
print(f"Task ID: {task.id}")
print("Waiting for task result...")

# Wait for a few seconds to see the task result
time.sleep(5)
print("\nTask should be processed by now. Check the database to verify the update.") 