import os
import sys
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to import backend modules
sys.path.append(os.path.abspath('.'))

from backend.db.models.call.call_log import CallLog
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository

async def test_external_call_id():
    """Test creating and retrieving a call with a string external_call_id."""
    
    # Database connection (from environment or use default for testing)
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/ai_dashboard")
    
    # Create engine and session
    engine = create_async_engine(db_url)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Create a test call with a string external_call_id
    external_call_id = "test_call_12345"
    test_uuid = str(uuid.uuid4())
    
    async with async_session() as session:
        # Create repository
        call_repository = PostgresCallRepository(session)
        
        # Create test data
        call_data = {
            "id": test_uuid,
            "branch_id": "8d8808a4-22f8-4af3-aec4-bab5b44b1aa7",  # Use an existing branch ID
            "gym_id": "facd154c-9be8-40fb-995f-27ea665d3a8b",     # Use an existing gym ID
            "lead_id": "15603c96-8d3a-49a9-9a0d-aca2189d04f9",    # Use an existing lead ID
            "call_type": "outbound",
            "call_status": "scheduled",
            "created_at": datetime.now(),
            "start_time": datetime.now(),
            "external_call_id": external_call_id
        }
        
        # Create the call
        print(f"Creating test call with ID: {test_uuid} and external_call_id: {external_call_id}")
        created_call = await call_repository.create_call(call_data)
        print(f"Created call: {created_call}")
        
        # Retrieve the call by external_call_id
        print(f"Retrieving call by external_call_id: {external_call_id}")
        retrieved_call = await call_repository.get_call_by_external_id(external_call_id)
        
        if retrieved_call:
            print(f"Successfully retrieved call by external_call_id: {retrieved_call}")
            assert retrieved_call['external_call_id'] == external_call_id
            print("Test passed! External call ID matches.")
        else:
            print(f"Failed to retrieve call by external_call_id: {external_call_id}")
            print("Test failed!")
        
        # Clean up the test data
        print(f"Cleaning up test data")
        await call_repository.delete_call(test_uuid)
        print("Test completed")

if __name__ == "__main__":
    asyncio.run(test_external_call_id()) 