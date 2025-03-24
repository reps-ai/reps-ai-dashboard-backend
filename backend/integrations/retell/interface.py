"""
Interface for the Retell Integration Service.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class RetellIntegration(ABC):
    """
    Interface for the Retell Integration Service.
    """
    
    @abstractmethod
    async def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the Retell API.
        
        Returns:
            Dictionary containing authentication result
        """
        pass
    
    @abstractmethod
    async def create_call(
        self, 
        lead_data: Dict[str, Any], 
        campaign_id: Optional[str] = None,
        max_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a call in Retell.
        
        Args:
            lead_data: Dictionary containing lead information
            campaign_id: Optional ID of the campaign
            max_duration: Optional maximum duration in seconds
            
        Returns:
            Dictionary containing call details
        """
        pass
    
    @abstractmethod
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get the status of a call.
        
        Args:
            call_id: ID of the call
            
        Returns:
            Dictionary containing call status
        """
        pass
    
    @abstractmethod
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End a call.
        
        Args:
            call_id: ID of the call
            
        Returns:
            Dictionary containing call result
        """
        pass
    
    @abstractmethod
    async def get_call_recording(self, call_id: str) -> Dict[str, Any]:
        """
        Get the recording for a call.
        
        Args:
            call_id: ID of the call
            
        Returns:
            Dictionary containing recording information
        """
        pass
    
    @abstractmethod
    async def get_call_transcript(self, call_id: str) -> List[Dict[str, Any]]:
        """
        Get the transcript for a call.
        
        Args:
            call_id: ID of the call
            
        Returns:
            List of transcript entries
        """
        pass
    
    @abstractmethod
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook from Retell.
        
        Args:
            webhook_data: Dictionary containing webhook data
            
        Returns:
            Dictionary containing processed webhook result
        """
        pass 