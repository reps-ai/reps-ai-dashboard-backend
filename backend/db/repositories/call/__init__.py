"""
Call repository initialization.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .implementations.postgres_call_repository import CallRepository
from .implementations.postgres_call_repository import PostgresCallRepository
from ...connections.database import get_db_session

async def create_call_repository(session: Optional[AsyncSession] = None) -> CallRepository:
    """
    Create and return a call repository instance.
    
    Args:
        session: Optional SQLAlchemy async session (will create one if not provided)
        
    Returns:
        An implementation of CallRepository
    """
    if not session:
        session = await get_db_session()
        
    return PostgresCallRepository(session)