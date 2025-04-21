"""
Factory for creating Campaign Service instances.
"""
from typing import Optional, Dict, Any
from .interface import CampaignService
from .implementation import DefaultCampaignService
from ...db.repositories.campaign import CampaignRepository
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

def create_campaign_service(
    campaign_repository: Optional[CampaignRepository] = None,
    config: Optional[Dict[str, Any]] = None
) -> CampaignService:
    """
    Create a Campaign Service instance.
    
    Args:
        campaign_repository: Optional repository for campaign operations
        config: Optional configuration for the service
        
    Returns:
        An instance of CampaignService
    """
    logger.info("Creating Campaign Service")
    
    # Create campaign repository if not provided
    if not campaign_repository:
        from ...db.repositories.campaign import create_campaign_repository
        campaign_repository = create_campaign_repository()
    
    # Create and return service
    return DefaultCampaignService(
        campaign_repository=campaign_repository
    )
