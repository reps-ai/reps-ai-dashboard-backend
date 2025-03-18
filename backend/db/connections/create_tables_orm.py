"""
Script to create tables in the Neon database using SQLAlchemy ORM.
This script creates all the tables defined in the SQLAlchemy models.
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.dialects import postgresql

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Base class
from backend.db.base import Base

# Import all models to ensure they're registered with the metadata
try:
    # Import models in the correct order to handle dependencies
    from backend.db.models.gym.branch import Branch
    from backend.db.models.user import User, user_branch
    from backend.db.models.lead.tag import Tag
    from backend.db.models.lead.lead import Lead
    from backend.db.models.lead.lead_tag import lead_tag
    from backend.db.models.call.call_settings import CallSettings
    from backend.db.models.call.call_log import CallLog
    from backend.db.models.call.follow_up_call import FollowUpCall
    from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
    from backend.db.models.ai_settings import AISettings
    
    print("Successfully imported all models")
except Exception as e:
    print(f"Error importing models: {e}")
    sys.exit(1)

def create_tables(drop_existing=False):
    """Create all tables in the database using SQLAlchemy."""
    # Load environment variables
    load_dotenv()
    
    # Get database connection string
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    print(f"Connecting to database...")
    
    # Create SQLAlchemy engine
    engine = create_engine(db_url)
    
    # Create all tables
    try:
        # Get all tables from metadata
        tables = Base.metadata.sorted_tables
        
        print(f"Found {len(tables)} tables to create")
        
        # If drop_existing is True, drop tables in reverse order
        if drop_existing:
            print("Dropping existing tables...")
            # Reverse the order for dropping to handle foreign key constraints
            for table in reversed(tables):
                try:
                    with engine.connect() as conn:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table.name} CASCADE"))
                        conn.commit()
                    print(f"✅ Dropped table: {table.name}")
                except Exception as e:
                    print(f"❌ Error dropping table {table.name}: {e}")
        
        # Create each table
        for table in tables:
            # Convert SQLAlchemy table to SQL string
            create_table_sql = str(CreateTable(table).compile(dialect=postgresql.dialect()))
            
            # Execute the SQL
            try:
                with engine.connect() as conn:
                    conn.execute(text(create_table_sql))
                    conn.commit()
                print(f"✅ Created table: {table.name}")
            except Exception as e:
                print(f"❌ Error creating table {table.name}: {e}")
    
    finally:
        # Close the connection
        engine.dispose()
        print("Database connection closed")

def main():
    """Main function to run the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create database tables using SQLAlchemy ORM')
    parser.add_argument('--drop', action='store_true', help='Drop existing tables before creating new ones')
    args = parser.parse_args()
    
    print("Starting table creation process...")
    create_tables(drop_existing=args.drop)
    print("Table creation completed")

if __name__ == "__main__":
    main() 