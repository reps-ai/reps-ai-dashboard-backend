"""
Campaign repository initialization.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .campaign_repository import CampaignRepository
from .implementations.postgres_campaign_repository import PostgresCampaignRepository
from ...connections.database import get_db_session

async def create_campaign_repository(session: Optional[AsyncSession] = None) -> CampaignRepository:
    """
    Create and return a campaign repository instance.
    
    Args:
        session: Optional SQLAlchemy async session (will create one if not provided)
        
    Returns:
        An implementation of CampaignRepository
    """
    if not session:
        session = await get_db_session()
        
    return PostgresCampaignRepository(session)