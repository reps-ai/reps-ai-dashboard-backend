"""
Factory for creating voice agent provider instances.
"""
from typing import Dict, Any, Optional

from .voice_agent_provider import VoiceAgentProvider
from .providers.retell import RetellVoiceAgentProvider
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

class VoiceAgentFactory:
    """
    Factory class for creating voice agent provider instances.
    This allows for easy switching between different providers.
    """
    
    @staticmethod
    async def create_provider(provider_type: str, config: Dict[str, Any]) -> VoiceAgentProvider:
        """
        Create and initialize a voice agent provider.

        Args:
            provider_type: Type of provider to create ("retell", etc.)
            config: Configuration for the provider

        Returns:
            Initialized voice agent provider instance

        Raises:
            ValueError: If the provider type is not supported
        """
        provider: Optional[VoiceAgentProvider] = None
        
        if provider_type.lower() == "retell":
            provider = RetellVoiceAgentProvider()
        else:
            raise ValueError(f"Unsupported voice agent provider: {provider_type}")
        
        # Initialize the provider with the provided configuration
        await provider.initialize(config)
        logger.info(f"Initialized {provider_type} voice agent provider")
        
        return provider 