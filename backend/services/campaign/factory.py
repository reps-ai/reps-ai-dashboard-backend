"""
Factory for creating campaign service instances.
"""
import logging
from typing import Optional, Dict, Any

from .interface import CampaignService
from .implementation import DefaultCampaignService
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

async def create_campaign_service_async(config: Optional[Dict[str, Any]] = None) -> CampaignService:
    """
    Create a campaign service instance asynchronously.
    
    Args:
        config: Optional service configuration
        
    Returns:
        Campaign service instance
    """
    logger.info("Creating Campaign Service")
    
    # Import repository module here to avoid circular imports
    from ...db.repositories.campaign import create_campaign_repository
    
    # Create repository
    campaign_repository = await create_campaign_repository()
    
    # Create and return service
    return DefaultCampaignService(
        campaign_repository=campaign_repository
    )

def create_campaign_service(config: Optional[Dict[str, Any]] = None) -> CampaignService:
    """
    Create a campaign service instance synchronously.
    Legacy method that should be avoided in async contexts.
    
    Args:
        config: Optional service configuration
        
    Returns:
        Campaign service instance
    """
    logger.info("Creating Campaign Service (sync method)")
    
    # Import repository module here to avoid circular imports
    from ...db.repositories.campaign import create_campaign_repository
    
    # Check if we're in an async context
    import asyncio
    if asyncio.get_event_loop().is_running():
        logger.warning("Called sync create_campaign_service in async context - this may fail")
        # Create dummy repository for now
        from ...db.repositories.campaign.implementations import PostgresCampaignRepository
        campaign_repository = PostgresCampaignRepository(None)
    else:
        # Use async_to_sync
        from asgiref.sync import async_to_sync
        try:
            campaign_repository = async_to_sync(create_campaign_repository)()
        except RuntimeError:
            logger.error("Failed to create campaign repository with async_to_sync - using dummy")
            from ...db.repositories.campaign.implementations import PostgresCampaignRepository
            campaign_repository = PostgresCampaignRepository(None)
    
    # Create and return service
    return DefaultCampaignService(
        campaign_repository=campaign_repository
    )
