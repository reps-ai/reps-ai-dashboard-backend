import asyncio
import uuid
from backend.services.call.implementation import DefaultCallService
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.db.connections.database import SessionLocal
from backend.services.call.factory import create_call_service

async def test_trigger_call():
    # Create session using the existing connection
    async with SessionLocal() as session:
        # Create call repository with session
        call_repository = PostgresCallRepository(session)
        
        # Create call service
        call_service = create_call_service(call_repository=call_repository)
        
        # Test lead ID
        lead_id = uuid.UUID("15603c96-8d3a-49a9-9a0d-aca2189d04f9")
        
        try:
            # Call the trigger_call method
            print(f"Triggering call for lead ID: {lead_id}")
            result = await call_service.trigger_call(lead_id=lead_id)
            
            # Print the result
            print(f"Call triggered successfully!")
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error triggering call: {str(e)}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_trigger_call())