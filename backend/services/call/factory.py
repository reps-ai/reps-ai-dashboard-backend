"""
Factory for creating Call Service instances.
"""
from typing import Optional, Dict, Any
from .interface import CallService
from .implementation import DefaultCallService
from ...db.repositories.call import CallRepository
from ...integrations.retell.factory import create_retell_integration
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

async def create_call_service_async(
    call_repository: Optional[CallRepository] = None,
    config: Optional[Dict[str, Any]] = None
) -> CallService:
    """
    Create a Call Service instance asynchronously.
    
    Args:
        call_repository: Optional repository for call operations
        config: Optional configuration for the service
        
    Returns:
        An instance of CallService
    """
    logger.info("Creating Call Service")
    
    # Create call repository if not provided
    if not call_repository:
        from ...db.repositories.call import create_call_repository
        call_repository = await create_call_repository()
    
    # Get configuration for retell integration if available
    enable_retell = config.get("enable_retell", True) if config else True
    
    # Create retell integration if enabled
    retell_integration = None
    if enable_retell:
        try:
            retell_integration = create_retell_integration()
            logger.info("Retell integration created successfully")
        except Exception as e:
            logger.error(f"Failed to create Retell integration: {str(e)}")
    
    # Create and return service
    return DefaultCallService(
        call_repository=call_repository,
        retell_integration=retell_integration
    )

def create_call_service(
    call_repository: Optional[CallRepository] = None,
    config: Optional[Dict[str, Any]] = None
) -> CallService:
    """
    Create a Call Service instance synchronously.
    
    This is a shortcut for testing/legacy code.
    New code should use create_call_service_async directly.
    
    Args:
        call_repository: Optional repository for call operations
        config: Optional configuration for the service
        
    Returns:
        An instance of CallService
    """
    # If we're in an async context, don't use async_to_sync
    import asyncio
    if asyncio.get_event_loop().is_running():
        # Create call repository with default session (will require an async context)
        if not call_repository:
            # For this to work, we need to be inside an async context already
            logger.warning("Creating call service in an async context using create_call_service - this may fail if not used in an async function")
            
            # Make a dummy repository for now since we can't get one asynchronously in a sync function
            from ...db.repositories.call.implementations import PostgresCallRepository
            call_repository = PostgresCallRepository(None)
    else:
        # We're not in an async context, so we can use async_to_sync
        from asgiref.sync import async_to_sync
        logger.warning("Creating call service using async_to_sync - this is inefficient and not recommended")
        try:
            from ...db.repositories.call import create_call_repository
            call_repository = async_to_sync(create_call_repository)()
        except RuntimeError:
            # If we get here, we're probably in a thread with an event loop already
            logger.error("Failed to create call repository using async_to_sync - creating dummy repository")
            from ...db.repositories.call.implementations import PostgresCallRepository
            call_repository = PostgresCallRepository(None)
    
    # Get configuration for retell integration if available
    enable_retell = config.get("enable_retell", True) if config else True
    
    # Create retell integration if enabled
    retell_integration = None
    if enable_retell:
        try:
            retell_integration = create_retell_integration()
            logger.info("Retell integration created successfully")
        except Exception as e:
            logger.error(f"Failed to create Retell integration: {str(e)}")
    
    # Create and return service
    return DefaultCallService(
        call_repository=call_repository,
        retell_integration=retell_integration
    )