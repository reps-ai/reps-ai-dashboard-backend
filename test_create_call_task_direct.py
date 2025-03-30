#!/usr/bin/env python
"""
Script to directly register and test the Celery task.
"""
import asyncio
import logging
import uuid
from celery import Celery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a simple Celery app
app = Celery('test_app')
app.config_from_object('backend.config.celery_config')

# Import the task function to manually register it
from backend.tasks.call.task_definitions import create_retell_call

# Now try to send a task directly
async def test_task():
    """Test sending the task directly."""
    try:
        # Create test data
        db_call_id = str(uuid.uuid4())
        lead_data = {
            "id": "15603c96-8d3a-49a9-9a0d-aca2189d04f9",
            "phone_number": "+919916968672",
            "name": "Test User",
            "gym_id": "facd154c-9be8-40fb-995f-27ea665d3a8b",
            "branch_id": "8d8808a4-22f8-4af3-aec4-bab5b44b1aa7",
            "interest": "Membership"
        }
        
        # Get registered tasks
        registered_tasks = app.tasks.keys()
        logger.info(f"Available tasks: {registered_tasks}")
        logger.info(f"Our task registered: {'call.create_retell_call' in registered_tasks}")
        
        # Try to apply the task directly
        logger.info(f"Applying task directly...")
        result = create_retell_call.apply_async(
            args=[db_call_id, lead_data, None],
            countdown=5
        )
        
        logger.info(f"Task ID: {result.id}")
        logger.info(f"Waiting for task to complete...")
        
        # Wait a bit for the task to run
        await asyncio.sleep(10)
        
        logger.info(f"Task state: {result.state}")
        
        # Try to check if the task succeeded
        try:
            task_result = result.get(timeout=1)
            logger.info(f"Task result: {task_result}")
        except Exception as e:
            logger.error(f"Error getting task result: {str(e)}")
        
        return result.id
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the async test function
    result = asyncio.run(test_task())
    print(f"Test completed with task ID: {result}") 