"""
Test script for triggering a call and handling the external_call_id properly.

This script directly uses the repository and service implementations to create and update a call.
"""
import asyncio
import uuid
from datetime import datetime

from backend.db.connections.database import SessionLocal
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.utils.logging.logger import get_logger
from backend.db.models.call.call_log import CallLog

logger = get_logger(__name__)

async def test_trigger_call():
    """Test the call creation and external_call_id handling directly with repository."""
    # Create database session
    db = SessionLocal()
    try:
        # Create repository directly
        call_repository = PostgresCallRepository(db)
        
        # Generate test data
        lead_id = str(uuid.uuid4())
        external_call_id = str(uuid.uuid4())
        
        # Create test call data
        call_data = {
            "lead_id": "15603c96-8d3a-49a9-9a0d-aca2189d04f9",  # Valid lead ID
            "branch_id": "8d8808a4-22f8-4af3-aec4-bab5b44b1aa7",  # Valid branch ID
            "gym_id": "facd154c-9be8-40fb-995f-27ea665d3a8b",  # Valid gym ID
            "call_status": "in_progress",
            "call_type": "outbound",
            "start_time": datetime.now(),
            "created_at": datetime.now(),
            "external_call_id": external_call_id,
            "human_notes": f"Test call created with external_call_id: {external_call_id}"
        }
        
        # Step 1: Create call directly with repository
        logger.info(f"Creating test call with data: {call_data}")
        new_call = await call_repository.create_call(call_data)
        call_id = new_call.get('id')
        
        logger.info(f"Created test call with ID: {call_id}")
        logger.info(f"External call ID: {new_call.get('external_call_id')}")
        
        # Step 2: Get the call by external ID to verify
        logger.info(f"Testing retrieval by external call ID: {external_call_id}")
        retrieved_call = await call_repository.get_call_by_external_id(external_call_id)
        
        if retrieved_call:
            logger.info(f"Success! Call retrieved by external ID: {retrieved_call.get('id')}")
        else:
            logger.error(f"Failed to retrieve call by external ID: {external_call_id}")
        
        # Step 3: Update the call with mock Retell data
        update_data = {
            "call_status": "completed",
            "end_time": datetime.now(),
            "duration": 120,
            "recording_url": f"https://storage.retell.ai/recordings/{external_call_id}.wav",
            "transcript": "Agent: Hello, this is Reps AI. How can I help you?\nUser: I'd like to know about membership options.",
            "summary": "User inquired about membership options",
            "sentiment": "positive"
        }
        
        logger.info(f"Updating call with mock Retell data")
        updated_call = await call_repository.update_call(call_id, update_data)
        
        if updated_call:
            logger.info(f"Call successfully updated: {updated_call.get('call_status')}")
            logger.info(f"Transcript length: {len(updated_call.get('transcript', ''))}")
        else:
            logger.error(f"Failed to update call {call_id}")
        
        # Explicitly commit changes
        await db.commit()
        
        return {
            "call_id": call_id,
            "external_call_id": external_call_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        await db.rollback()
        raise
    finally:
        # Close the session
        await db.close()

if __name__ == "__main__":
    # Run the async test function
    result = asyncio.run(test_trigger_call())
    print(f"Test completed with result: {result}") 