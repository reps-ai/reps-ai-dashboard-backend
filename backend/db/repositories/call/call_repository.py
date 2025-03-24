"""
Call repository interface defining the contract for call operations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class CallRepository(ABC):
    """
    Abstract base class defining the interface for call repository operations.
    Any concrete implementation must implement all these methods.
    """
    
    @abstractmethod
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call record.

        Args:
            call_data: Dictionary containing call details

        Returns:
            Dict containing the created call data
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
    async def get_calls_by_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Get all calls for a campaign.

        Args:
            campaign_id: Unique identifier of the campaign

        Returns:
            List of call data associated with the campaign
        """
        pass

    @abstractmethod
    async def get_calls_by_lead(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Get all calls for a lead.

        Args:
            lead_id: Unique identifier of the lead

        Returns:
            List of call data associated with the lead
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
        Get calls within a date range.

        Args:
            gym_id: Unique identifier of the gym
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            List of call data within the date range
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
    async def save_call_recording(self, call_id: str, recording_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
    async def save_call_transcript(self, call_id: str, transcript: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Save call transcript.

        Args:
            call_id: Unique identifier of the call
            transcript: List of transcript segments

        Returns:
            Updated call data if successful, None if call not found
        """
        pass

    @abstractmethod
    async def update_call_metrics(self, call_id: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update call metrics (duration, sentiment, etc.).

        Args:
            call_id: Unique identifier of the call
            metrics: Dictionary containing metric updates

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
        gym_id: str, 
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get scheduled calls for a time period.

        Args:
            gym_id: Unique identifier of the gym
            start_time: Start of the time period
            end_time: End of the time period

        Returns:
            List of scheduled call data
        """
        pass

    @abstractmethod
    async def get_calls_by_outcome(self, gym_id: str, outcome: str) -> List[Dict[str, Any]]:
        """
        Get calls by outcome.

        Args:
            gym_id: Unique identifier of the gym
            outcome: Outcome to filter by

        Returns:
            List of call data with the specified outcome
        """
        pass

    @abstractmethod
    async def get_call_summary(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get call summary including transcript analysis.

        Args:
            call_id: Unique identifier of the call

        Returns:
            Call summary data if found, None otherwise
        """
        pass 