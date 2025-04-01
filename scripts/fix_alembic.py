"""
Script to fix Alembic migration issues by resetting to the current head.
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Remove asyncpg prefix if present
if "+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

def fix_alembic_version():
    """Reset alembic_version table to the current head revision."""
    try:
        # Connect to the database
        print(f"Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Get the current head from alembic history
        print("Getting current head revision...")
        current_head = "834c466287a3"  # This is your current head based on the alembic history output
        
        # Check if the version table exists
        cursor.execute("SELECT to_regclass('public.alembic_version')")
        table_exists = cursor.fetchone()[0] is not None
        
        if not table_exists:
            print("Creating alembic_version table...")
            cursor.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
            cursor.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", (current_head,))
        else:
            # Clear and update the version table
            print(f"Updating alembic_version table to head revision: {current_head}")
            cursor.execute("DELETE FROM alembic_version")
            cursor.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", (current_head,))
        
        conn.commit()
        print("Successfully fixed alembic version!")
        
    except Exception as e:
        print(f"Error fixing alembic version: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    fix_alembic_version()
