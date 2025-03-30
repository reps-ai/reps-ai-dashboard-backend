"""
Script to trigger a test call using real lead data.
"""
import asyncio
from datetime import datetime
from uuid import UUID

from backend.db.connections.database import SessionLocal
from backend.db.repositories.call.implementations import PostgresCallRepository
from backend.services.call.implementation import DefaultCallService
from backend.integrations.retell.implementation import RetellImplementation
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

# Test data
LEAD_ID = "15603c96-8d3a-49a9-9a0d-aca2189d04f9"
GYM_ID = "facd154c-9be8-40fb-995f-27ea665d3a8b"
BRANCH_ID = "8d8808a4-22f8-4af3-aec4-bab5b44b1aa7"
TEST_CAMPAIGN_ID = "9427e0d4-bede-479c-a07a-2078592c6cd5"  # Added test campaign ID

LEAD_DATA = {
    "id": LEAD_ID,
    "phone_number": "+919916968672",  # Adding + and country code
    "name": "Aditya",
    "gym_id": GYM_ID,
    "branch_id": BRANCH_ID,
    "interest": "Test call"  # Adding an interest field
}

async def trigger_test_call():
    """Trigger a test call using the CallService."""
    try:
        # Get database session
        db = SessionLocal()
        
        try:
            # Initialize repository and services
            call_repository = PostgresCallRepository(db)
            retell_integration = RetellImplementation()  # Using RetellImplementation instead of interface
            call_service = DefaultCallService(
                call_repository=call_repository,
                retell_integration=retell_integration
            )
            
            logger.info("Triggering test call...")
            logger.info(f"Lead data: {LEAD_DATA}")
            
            # Trigger the call with campaign_id
            result = await call_service.trigger_call(
                lead_id=LEAD_ID,
                campaign_id=TEST_CAMPAIGN_ID,  # Added campaign_id
                lead_data=LEAD_DATA
            )
            
            logger.info(f"Call triggered successfully!")
            logger.info(f"Initial call record: {result}")
            
            # Wait a bit and check call status
            await asyncio.sleep(5)
            
            # Get updated call status
            updated_call = await call_service.get_call(result["id"])
            logger.info(f"Updated call status: {updated_call}")
            
            return result
            
        finally:
            await db.close()
            
    except Exception as e:
        logger.error(f"Error triggering test call: {str(e)}")
        raise e

if __name__ == "__main__":
    asyncio.run(trigger_test_call())
