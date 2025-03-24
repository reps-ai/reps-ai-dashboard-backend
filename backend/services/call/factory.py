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

def create_call_service(
    call_repository: Optional[CallRepository] = None,
    config: Optional[Dict[str, Any]] = None
) -> CallService:
    """
    Create a Call Service instance.
    
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
        call_repository = create_call_repository()
    
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