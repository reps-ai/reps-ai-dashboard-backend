"""
Voice agent provider interface defining the contract for voice agent operations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncGenerator

class VoiceAgentProvider(ABC):
    """
    Abstract base class defining the interface for voice agent provider operations.
    Any concrete implementation (Retell, Deepgram, etc.) must implement all these methods.
    """
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the voice agent provider with configuration.

        Args:
            config: Dictionary containing provider-specific configuration
        """
        pass
    
    @abstractmethod
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call with the voice agent provider.

        Args:
            call_data: Dictionary containing call details including:
                - lead_id: ID of the lead being called
                - phone_number: Phone number to call
                - campaign_id: ID of the campaign this call belongs to
                - agent_config: Configuration for the voice agent

        Returns:
            Dictionary containing provider-specific call details including:
                - provider_call_id: Provider's unique identifier for the call
                - status: Initial status of the call
        """
        pass
    
    @abstractmethod
    async def end_call(self, provider_call_id: str) -> Dict[str, Any]:
        """
        End an active call.

        Args:
            provider_call_id: Provider's unique identifier for the call

        Returns:
            Dictionary containing call outcome details
        """
        pass
    
    @abstractmethod
    async def get_call_status(self, provider_call_id: str) -> Dict[str, Any]:
        """
        Get the current status of a call.

        Args:
            provider_call_id: Provider's unique identifier for the call

        Returns:
            Dictionary containing call status details
        """
        pass
    
    @abstractmethod
    async def get_call_recording(self, provider_call_id: str) -> Dict[str, Any]:
        """
        Get the recording for a completed call.

        Args:
            provider_call_id: Provider's unique identifier for the call

        Returns:
            Dictionary containing recording details including:
                - recording_url: URL to the recording file
                - duration: Duration of the recording in seconds
                - format: Format of the recording file
        """
        pass
    
    @abstractmethod
    async def get_call_transcript(self, provider_call_id: str) -> List[Dict[str, Any]]:
        """
        Get the transcript for a completed call.

        Args:
            provider_call_id: Provider's unique identifier for the call

        Returns:
            List of transcript segments, each containing:
                - speaker: Who is speaking ("agent" or "user")
                - text: The text spoken
                - start_time: Start time of the segment in seconds
                - end_time: End time of the segment in seconds
        """
        pass
    
    @abstractmethod
    async def stream_call_audio(self, provider_call_id: str) -> AsyncGenerator[bytes, None]:
        """
        Stream the audio of an active call.

        Args:
            provider_call_id: Provider's unique identifier for the call

        Yields:
            Audio chunks as bytes
        """
        pass
    
    @abstractmethod
    async def update_agent_config(self, provider_call_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the configuration of an active voice agent.

        Args:
            provider_call_id: Provider's unique identifier for the call
            agent_config: New configuration for the voice agent

        Returns:
            Dictionary containing updated agent details
        """
        pass
    
    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get a list of available voice options from the provider.

        Returns:
            List of voice options, each containing:
                - voice_id: Unique identifier for the voice
                - name: Display name of the voice
                - gender: Gender of the voice
                - language: Language of the voice
                - additional provider-specific details
        """
        pass
    
    @abstractmethod
    async def validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Validate that a webhook request is authentic and from the provider.

        Args:
            webhook_data: Dictionary containing webhook request data

        Returns:
            True if the webhook is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def parse_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a webhook request from the provider.

        Args:
            webhook_data: Dictionary containing webhook request data

        Returns:
            Dictionary containing parsed webhook data in a standardized format
        """
        pass 