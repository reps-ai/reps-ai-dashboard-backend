"""
Script to create tables in the Neon database using asyncpg.
This script creates all the tables defined in the SQLAlchemy models.
"""
import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

# Import the Base class and all models to ensure they're registered with the metadata
from ..base import Base
from ..models.lead.lead import Lead
from ..models.lead.tag import Tag
from ..models.lead.lead_tag import lead_tag
from ..models.call.call_settings import CallSettings
from ..models.call.call_log import CallLog
from ..models.call.follow_up_call import FollowUpCall
from ..models.user import User, user_branch
from ..models.gym.branch import Branch
from ..models.campaign.follow_up_campaign import FollowUpCampaign
from ..models.ai_settings import AISettings

async def create_tables():
    """Create all tables in the database."""
    # Load environment variables
    load_dotenv()
    
    # Get database connection string
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Connect to the database
    conn = await asyncpg.connect(db_url)
    
    try:
        # Get all tables from metadata
        tables = Base.metadata.sorted_tables
        
        # Create each table
        for table in tables:
            # Convert SQLAlchemy table to SQL string
            create_table_sql = str(CreateTable(table).compile(dialect=postgresql.dialect()))
            
            # Execute the SQL
            try:
                await conn.execute(create_table_sql)
                print(f"Created table: {table.name}")
            except Exception as e:
                print(f"Error creating table {table.name}: {e}")
    
    finally:
        # Close the connection
        await conn.close()

async def main():
    """Main function to run the script."""
    await create_tables()
    print("Table creation completed")

if __name__ == "__main__":
    asyncio.run(main())
