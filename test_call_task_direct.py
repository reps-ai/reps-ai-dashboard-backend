#!/usr/bin/env python
"""
Test script to directly invoke the create_retell_call task.
"""
import asyncio
import logging
import uuid
from datetime import datetime

from backend.celery_app import app as celery_app
from backend.db.connections.database import SessionLocal
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_test_call():
    """Create a test call and trigger the Celery task directly."""
    try:
        # Get database session
        db = SessionLocal()
        
        try:
            # Initialize repository
            call_repository = PostgresCallRepository(db)
            
            # Use the valid IDs from your database
            lead_id = "15603c96-8d3a-49a9-9a0d-aca2189d04f9"
            branch_id = "8d8808a4-22f8-4af3-aec4-bab5b44b1aa7"
            gym_id = "facd154c-9be8-40fb-995f-27ea665d3a8b"
            
            # Create lead data with valid phone number
            lead_data = {
                "id": lead_id,
                "phone_number": "+919916968672",  # Your phone number
                "name": "Test User",
                "gym_id": gym_id,
                "branch_id": branch_id,
                "interest": "Membership"
            }
            
            # Create call data
            call_data = {
                "lead_id": lead_id,
                "gym_id": gym_id,
                "branch_id": branch_id,
                "call_status": "scheduled",
                "call_type": "outbound",
            }
            
            # Create call using repository (initial database entry)
            logger.info("Creating call record...")
            db_call = await call_repository.create_call(call_data)
            call_id = str(db_call.get("id"))
            
            logger.info(f"Created call record with ID: {call_id}")
            
            # Check registered tasks
            registered_tasks = celery_app.tasks.keys()
            logger.info(f"All registered tasks: {registered_tasks}")
            logger.info(f"Task 'call.create_retell_call' registered: {'call.create_retell_call' in registered_tasks}")
            
            # Directly invoke the Celery task (this will be executed by a worker)
            logger.info(f"Calling create_retell_call task for call ID: {call_id}")
            task_result = celery_app.send_task(
                'call.create_retell_call',
                args=[call_id, lead_data, None]  # No campaign ID
            )
            
            logger.info(f"Task queued with ID: {task_result.id}")
            logger.info("Waiting 10 seconds to let the task complete...")
            
            # Wait for the task to complete
            await asyncio.sleep(10)
            
            # Check if call was updated
            updated_call = await call_repository.get_call_by_id(call_id)
            
            logger.info(f"Updated call status: {updated_call.get('call_status')}")
            logger.info(f"External call ID: {updated_call.get('external_call_id')}")
            
            return updated_call
            
        finally:
            # Close the session
            await db.close()
            
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise e

if __name__ == "__main__":
    # Run the async test function
    result = asyncio.run(create_test_call())
    print(f"\nTest completed with result: {result}") 