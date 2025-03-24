from ...connections.database import get_db
from sqlalchemy import text
import asyncio

async def test_database_connection():
    """Test that we can connect to the database."""
    async with get_db() as db:
        print("Successfully connected to the database!")
        
        # Try a simple query
        result = await db.execute(text("SELECT 1"))
        value = result.scalar()
        print(f"Query result: {value}")

if __name__ == "__main__":
    asyncio.run(test_database_connection()) 