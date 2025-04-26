"""
Lead repository initialization.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .implementations.postgres_lead_repository import LeadRepository
from .implementations.postgres_lead_repository import PostgresLeadRepository
from ...connections.database import get_db_session

async def create_lead_repository(session: Optional[AsyncSession] = None) -> LeadRepository:
    """
    Create and return a lead repository instance.
    
    Args:
        session: Optional SQLAlchemy async session (will create one if not provided)
        
    Returns:
        An implementation of LeadRepository
    """
    # CRITICAL: Only create a new session if one isn't provided
    if not session:
        session = await get_db_session()
        
    return PostgresLeadRepository(session)