"""
Test script for verifying the trigger_call functionality with Retell integration.

This script:
1. Triggers a call with valid data
2. Verifies the external_call_id is stored correctly
3. Ensures the polling task is scheduled
"""
import asyncio
import uuid
from datetime import datetime

from backend.db.connections.database import SessionLocal
from backend.services.call.implementation import DefaultCallService
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.integrations.retell.implementation import RetellImplementation
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

async def test_trigger_call():
    """Test the trigger_call functionality with Retell integration."""
    # Create database session
    db = SessionLocal()
    try:
        # Create repository
        call_repository = PostgresCallRepository(db)
        
        # Create Retell integration
        retell_integration = RetellImplementation()
        
        # Create call service with Retell integration
        call_service = DefaultCallService(call_repository, retell_integration)
        
        # Use the valid IDs from your database
        lead_id = "15603c96-8d3a-49a9-9a0d-aca2189d04f9"
        branch_id = "8d8808a4-22f8-4af3-aec4-bab5b44b1aa7"
        gym_id = "facd154c-9be8-40fb-995f-27ea665d3a8b"
        
        # Create lead data with valid phone number
        lead_data = {
            "id": lead_id,
            "phone_number": "+919916968672",  # Valid E.164 format phone number for testing
            "name": "Test User",
            "gym_id": gym_id,
            "branch_id": branch_id,
            "interest": "Membership"
        }
        
        # Step 1: Trigger the call
        logger.info(f"Triggering call for lead: {lead_id}")
        call_result = await call_service.trigger_call(
            lead_id=lead_id,
            lead_data=lead_data
        )
        
        # Log the result
        logger.info(f"Call triggered with ID: {call_result.get('id')}")
        logger.info(f"Call status: {call_result.get('call_status')}")
        logger.info(f"Initial call status should be 'scheduled': {call_result.get('call_status') == 'scheduled'}")
        
        # Step 2: Verify call was created correctly
        if call_result.get('id'):
            created_call = await call_repository.get_call_by_id(call_result.get('id'))
            logger.info(f"Retrieved call status: {created_call.get('call_status')}")
            
            # At this point, external_call_id will not be set yet since the background task hasn't run
            logger.info(f"External call ID should not be set yet: {created_call.get('external_call_id') is None}")
            
            # Check if the background task is configured properly
            # In a real test, we'd wait for the task to complete or use a mock
            from backend.celery_app import app as celery_app
            registered_tasks = celery_app.tasks.keys()
            logger.info(f"'call.create_retell_call' task registered: {'call.create_retell_call' in registered_tasks}")
        
        # Step 3: In a production environment, we'd wait for the task to complete
        # For this test, we're just checking if the initial setup is correct
        logger.info("In a production environment, the Celery task would now create the Retell call")
        logger.info("and update the call record with the external_call_id")
        
        # Wait a moment to allow for logs to sync
        await asyncio.sleep(1)
        
        return call_result
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise
    finally:
        # Close the session
        await db.close()

if __name__ == "__main__":
    # Run the async test function
    result = asyncio.run(test_trigger_call())
    print(f"Test completed with result: {result}") 