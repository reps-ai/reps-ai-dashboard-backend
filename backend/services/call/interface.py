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
    async def trigger_call(self, lead_id: str, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger a call to a lead.
        
        Args:
            lead_id: ID of the lead to call
            campaign_id: Optional ID of the campaign
            
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
    async def get_calls_by_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Get calls for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            List of calls for the campaign
        """
        pass
    
    @abstractmethod
    async def get_calls_by_lead(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Get calls for a lead.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            List of calls for the lead
        """
        pass
    
    @abstractmethod
    async def get_calls_by_date_range(
        self, 
        gym_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get calls for a gym within a date range.
        
        Args:
            gym_id: ID of the gym
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            List of calls within the date range
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