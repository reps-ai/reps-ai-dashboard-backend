"""
Factory for creating campaign repository instances.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .campaign_repository import CampaignRepository
from .implementations.postgres_campaign_repository import PostgresCampaignRepository
from ...connections.database import get_db_session
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

async def create_campaign_repository(session: Optional[AsyncSession] = None) -> CampaignRepository:
    """
    Create a campaign repository instance.
    
    Args:
        session: Optional database session to use
        
    Returns:
        Campaign repository instance
    """
    # If session not provided, create a new one
    if session is None:
        session = await get_db_session()
        
    logger.info("Creating campaign repository")
    return PostgresCampaignRepository(session)
