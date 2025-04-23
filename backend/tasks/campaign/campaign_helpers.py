"""
Helper utilities for campaign tasks.
"""
from contextlib import asynccontextmanager
from ...db.connections.database import get_db
from ...utils.logging.logger import get_logger

# Configure logging
logger = get_logger(__name__)

@asynccontextmanager
async def db_session():
    """
    Context manager to properly handle the database session.
    """
    db_gen = get_db()
    try:
        session = await db_gen.__anext__()
        yield session
    finally:
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass
