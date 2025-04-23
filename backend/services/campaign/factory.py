"""
Factory for creating campaign service instances.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .interface import CampaignService
from .implementation import DefaultCampaignService
from ...db.repositories.campaign import create_campaign_repository
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

async def create_campaign_service_async(session: Optional[AsyncSession] = None) -> CampaignService:
    """
    Create a campaign service instance asynchronously.
    
    Args:
        session: Optional database session
        
    Returns:
        Campaign service instance
    """
    logger.info("Creating Campaign Service")
    
    # Create repository
    campaign_repository = await create_campaign_repository(session)
    
    # Create service
    return DefaultCampaignService(campaign_repository)

def create_campaign_service() -> CampaignService:
    """
    Create a campaign service instance synchronously.
    
    This is a shortcut for testing/legacy code.
    New code should use create_campaign_service_async directly.
    
    Returns:
        Campaign service instance
    """
    import asyncio
    from asgiref.sync import async_to_sync
    
    # Check if we're in an async context
    if asyncio.get_event_loop().is_running():
        logger.warning("Creating campaign service in async context using sync function - this may cause issues")
        # For this to work correctly, we need to be inside an already running async context
        
        # Since we can't await in a sync function, we need to create a repository synchronously
        from ...db.repositories.campaign.implementations import PostgresCampaignRepository
        campaign_repository = PostgresCampaignRepository(None)  # This is not ideal
    else:
        # Not in async context, use async_to_sync
        try:
            campaign_repository = async_to_sync(create_campaign_repository)()
        except RuntimeError:
            # If we get here, we're probably in a thread with an event loop
            logger.error("Failed to create repository with async_to_sync - creating dummy repository")
            from ...db.repositories.campaign.implementations import PostgresCampaignRepository
            campaign_repository = PostgresCampaignRepository(None)
    
    return DefaultCampaignService(campaign_repository)
