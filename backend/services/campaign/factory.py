"""
Factory for creating Campaign Service instances.
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from .interface import CampaignService
from .implementation import DefaultCampaignService
from ...db.repositories.campaign import CampaignRepository
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

async def create_campaign_service_async(
    campaign_repository: Optional[CampaignRepository] = None,
    config: Optional[Dict[str, Any]] = None,
    session: Optional[AsyncSession] = None  # Add session parameter
) -> CampaignService:
    """
    Create a Campaign Service instance asynchronously.
    
    Args:
        campaign_repository: Optional repository for campaign operations
        config: Optional configuration for the service
        session: Optional database session to use
        
    Returns:
        An instance of CampaignService
    """
    logger.info("Creating Campaign Service")
    
    # Create campaign repository if not provided
    if not campaign_repository:
        from ...db.repositories.campaign import create_campaign_repository
        # Explicitly pass session if provided
        if session:
            campaign_repository = await create_campaign_repository(session=session)
        else:
            campaign_repository = await create_campaign_repository()
    
    # Create the campaign service with just the repository
    campaign_service = DefaultCampaignService(campaign_repository)
    
    # Import call service here to prevent circular imports
    from ...services.call.factory import create_call_service_async
    
    # Important: Pass the same session to the call service
    call_service = await create_call_service_async(
        config=config,
        session=session  # Pass the same session to call service
    )
    
    # Set the call service using the setter method
    campaign_service.set_call_service(call_service)
    
    # Log whether we have a Retell integration available
    has_retell = hasattr(call_service, 'retell_integration') and call_service.retell_integration is not None
    logger.info(f"Campaign service call_service set with Retell integration: {has_retell}")
    logger.debug(f"Campaign service call_service set with Retell integration: {has_retell}")
    
    logger.info(f"Campaign service created with Retell integration: {has_retell}")
    logger.debug(f"Campaign service created with Retell integration: {has_retell}")
    
    return campaign_service

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
    
    # Import create_campaign_repository function here to avoid the undefined error
    from ...db.repositories.campaign import create_campaign_repository
    
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
    
    # Create campaign service
    campaign_service = DefaultCampaignService(campaign_repository)
    
    try:
        # Create and attach call service with Retell integration
        from ...services.call.factory import create_call_service
        call_service = create_call_service()
        # Use setter method
        campaign_service.set_call_service(call_service)
        
        # Extra debugging
        has_retell = hasattr(call_service, 'retell_integration') and call_service.retell_integration is not None
        logger.info(f"Campaign service created with Retell integration: {has_retell}")
        print(f"DEBUG - Campaign service created with Retell integration: {has_retell}")
        if not has_retell:
            print(f"DEBUG - call_service attributes: {dir(call_service)}")
            
    except Exception as e:
        logger.error(f"Error attaching call service: {str(e)}")
        print(f"DEBUG - Error attaching call service: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    return campaign_service
