"""
Interface for the Call Processing Service.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class CallService(ABC):
    """
    Interface for the Call Processing Service.
    """
    
    @abstractmethod
    async def trigger_call(self, lead_id: str, campaign_id: Optional[str] = None, lead_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a call to a lead.
        
        Args:
            lead_id: ID of the lead to call
            campaign_id: Optional ID of the campaign
            lead_data: Optional pre-loaded lead data
            
        Returns:
            Dictionary containing call details
        """
        pass
    
    @abstractmethod
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get call details by ID.
        
        Args:
            call_id: ID of the call
            
        Returns:
            Dictionary containing call details
        """
        pass
    
    @abstractmethod
    async def update_call(self, call_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update call information.
        
        Args:
            call_id: ID of the call
            call_data: Dictionary containing updated call information
            
        Returns:
            Dictionary containing the updated call details
        """
        pass
    
    @abstractmethod
    async def process_call_recording(self, call_id: str, recording_url: str) -> Dict[str, Any]:
        """
        Process a call recording.
        
        Args:
            call_id: ID of the call
            recording_url: URL of the recording
            
        Returns:
            Dictionary containing processed call details
        """
        pass
    
    @abstractmethod
    async def generate_call_summary(self, call_id: str, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary from a call transcript.
        
        Args:
            call_id: ID of the call
            transcript: List of transcript entries
            
        Returns:
            Dictionary containing the summary and other analysis results
        """
        pass
    
    @abstractmethod
    async def get_calls_by_campaign(
        self, 
        campaign_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:  # Changed from List[Dict[str, Any]]
        """
        Get calls for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info  # Updated return description
        """
        pass
    
    @abstractmethod
    async def get_calls_by_lead(
        self, 
        lead_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:  # Changed from List[Dict[str, Any]]
        """
        Get calls for a lead.
        
        Args:
            lead_id: ID of the lead
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info  # Updated return description
        """
        pass
    
    @abstractmethod
    async def get_calls_by_date_range(
        self, 
        gym_id: str, 
        start_date: datetime, 
        end_date: datetime,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:  # Changed from List[Dict[str, Any]]
        """
        Get calls for a gym within a date range.
        
        Args:
            gym_id: ID of the gym
            start_date: Start date for the range
            end_date: End date for the range
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info  # Updated return description
        """
        pass
    
    @abstractmethod
    async def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event from the call provider.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            Dictionary containing the processed event result
        """
        pass
    
    @abstractmethod
    async def get_filtered_calls(
        self, 
        gym_id: str,
        page: int = 1,
        page_size: int = 50,
        lead_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        direction: Optional[str] = None,
        outcome: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get filtered calls with all possible combinations of filters.
        
        Args:
            gym_id: ID of the gym (required for security)
            page: Page number
            page_size: Page size
            lead_id: Optional ID of the lead to filter by
            campaign_id: Optional ID of the campaign to filter by
            direction: Optional call direction to filter by (inbound/outbound)
            outcome: Optional call outcome to filter by
            start_date: Optional start date for date range filtering
            end_date: Optional end date for date range filtering
            
        Returns:
            Dictionary with calls and pagination info
        
        Raises:
            ValueError: If an error occurs during retrieval
        """
        pass
    
    @abstractmethod
    async def delete_call(self, call_id: str) -> Dict[str, Any]:
        """
        Delete a call record.
        
        Args:
            call_id: ID of the call to delete
            
        Returns:
            Dictionary with status information
            
        Raises:
            ValueError: If call not found or other error occurs
        """
        pass