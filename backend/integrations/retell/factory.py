"""
Factory for creating Retell Integration instances.
"""
from typing import Optional, Dict, Any
from .interface import RetellIntegration
from .implementation import RetellImplementation
from ...utils.logging.logger import get_logger
import os

logger = get_logger(__name__)

def create_retell_integration(
    config: Optional[Dict[str, Any]] = None
) -> RetellIntegration:
    """
    Create a Retell Integration instance.
    
    Args:
        config: Optional configuration for the integration
        
    Returns:
        An instance of RetellIntegration
    """
    logger.info("Creating Retell Integration")
    
    try:
        # Create and return the integration
        integration = RetellImplementation()
        logger.info("Retell Integration created successfully")
        return integration
    except Exception as e:
        logger.error(f"Failed to create Retell integration: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Print to stdout for Docker logs as well
        print("Failed to create Retell integration:", str(e))
        print(traceback.format_exc())
        raise