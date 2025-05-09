"""
Interface for call repository operations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class CallRepository(ABC):
    """Interface for call repository operations."""
    
    @abstractmethod
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call record.
        
        Args:
            call_data: Dictionary containing call details
            
        Returns:
            Dictionary containing the created call data
        """
        pass
    
    @abstractmethod
    async def get_call_by_id(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get call details by ID.
        
        Args:
            call_id: Unique identifier of the call
            
        Returns:
            Call data if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_call_by_external_id(self, external_call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a call by external call ID.
        
        Args:
            external_call_id: External ID of the call (e.g., from Retell)
        
        Returns:
            Dictionary containing call data, or None if not found
        """
        pass
    
    @abstractmethod
    async def update_call(self, call_id: str, call_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update call details.
        
        Args:
            call_id: Unique identifier of the call
            call_data: Dictionary containing updated call details
            
        Returns:
            Updated call data if successful, None if call not found
        """
        pass
    
    @abstractmethod
    async def delete_call(self, call_id: str) -> bool:
        """
        Delete a call record.
        
        Args:
            call_id: Unique identifier of the call
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_calls_by_campaign(
        self,
        campaign_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get all calls for a campaign.
        
        Args:
            campaign_id: Unique identifier of the campaign
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        pass
    
    @abstractmethod
    async def get_calls_by_lead(
        self,
        lead_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get all calls for a lead.
        
        Args:
            lead_id: Unique identifier of the lead
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        pass
    
    @abstractmethod
    async def get_calls_by_date_range(
        self,
        branch_id: str,  # Should be branch_id to match implementation
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get calls within a date range.
        
        Args:
            branch_id: Unique identifier of the gym
            start_date: Start of the date range
            end_date: End of the date range
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        pass
    
    @abstractmethod
    async def update_call_status(self, call_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update call status.
        
        Args:
            call_id: Unique identifier of the call
            status: New status
            
        Returns:
            Updated call data if successful, None if call not found
        """
        pass
    
    @abstractmethod
    async def update_call_outcome(self, call_id: str, outcome: str) -> Optional[Dict[str, Any]]:
        """
        Update call outcome.
        
        Args:
            call_id: Unique identifier of the call
            outcome: New outcome
            
        Returns:
            Updated call data if successful, None if call not found
        """
        pass
    
    @abstractmethod
    async def save_call_recording(
        self,
        call_id: str,
        recording_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Save call recording information.
        
        Args:
            call_id: Unique identifier of the call
            recording_data: Dictionary containing recording details
            
        Returns:
            Updated call data if successful, None if call not found
        """
        pass
    
    @abstractmethod
    async def save_call_transcript(
        self,
        call_id: str,
        transcript_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Save call transcript.
        
        Args:
            call_id: Unique identifier of the call
            transcript_data: Dictionary containing transcript details
            
        Returns:
            Updated call data if successful, None if call not found
        """
        pass
    
    @abstractmethod
    async def update_call_metrics(
        self,
        call_id: str,
        metrics_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update call metrics (duration, sentiment, etc.).
        
        Args:
            call_id: Unique identifier of the call
            metrics_data: Dictionary containing metric updates
            
        Returns:
            Updated call data if successful, None if call not found
        """
        pass
    
    @abstractmethod
    async def get_active_calls(self, gym_id: str) -> List[Dict[str, Any]]:
        """
        Get all active calls for a gym.
        
        Args:
            gym_id: Unique identifier of the gym
            
        Returns:
            List of active call data
        """
        pass
    
    @abstractmethod
    async def get_scheduled_calls(
        self,
        branch_id: str,  # Changed from gym_id to branch_id
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get scheduled calls for a time period.
        
        Args:
            branch_id: Branch ID to filter by
            start_time: Start of the time period
            end_time: End of the time period
            
        Returns:
            List of scheduled call data
        """
        pass
    
    @abstractmethod
    async def get_calls_by_outcome(
        self,
        branch_id: str,  # Changed from gym_id to branch_id to match implementation
        outcome: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get calls by outcome.
        
        Args:
            branch_id: Unique identifier of the branch  # Updated param name in docstring
            outcome: Outcome to filter by
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        pass
    
    @abstractmethod
    async def get_calls_with_filters(
        self,
        branch_id: str,  # Changed from gym_id to branch_id
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
        Get calls with combined filtering at the database level.
        
        Args:
            branch_id: ID of the branch (required for security)
            page: Page number
            page_size: Page size
            lead_id: Optional lead ID to filter by
            campaign_id: Optional campaign ID to filter by
            direction: Optional call direction to filter by (inbound/outbound)
            outcome: Optional outcome to filter by
            start_date: Optional start date for date range filtering
            end_date: Optional end date for date range filtering
            
        Returns:
            Dictionary containing calls and pagination info
        """
        pass