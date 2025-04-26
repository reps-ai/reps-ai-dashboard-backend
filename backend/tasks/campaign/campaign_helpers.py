"""
Helper utilities for campaign tasks.
"""
from contextlib import asynccontextmanager
from ...db.connections.database import SessionLocal, get_db_session
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def db_session():
    """Context manager for database sessions in campaign tasks."""
    # Create a session directly
    session = SessionLocal()
    try:
        # Yield the session for use
        yield session
        # Commit any pending changes
        await session.commit()
    except Exception as e:
        # Rollback on error
        await session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        # Always close the session
        await session.close()
