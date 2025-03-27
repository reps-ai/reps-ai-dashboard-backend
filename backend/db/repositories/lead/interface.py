"""
Lead repository interface defining the contract for lead operations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class LeadRepository(ABC):
    """
    Abstract base class defining the interface for lead repository operations.
    Any concrete implementation must implement all these methods.
    """
    
    @abstractmethod
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new lead.

        Args:
            lead_data: Dictionary containing lead details

        Returns:
            Dict containing the created lead data
        """
        pass

    @abstractmethod
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Get lead details by ID.

        Args:
            lead_id: Unique identifier of the lead

        Returns:
            Lead data if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update lead details.

        Args:
            lead_id: Unique identifier of the lead
            lead_data: Dictionary containing updated lead details

        Returns:
            Updated lead data if successful, None if lead not found
        """
        pass

    @abstractmethod
    async def delete_lead(self, lead_id: str) -> bool:
        """
        Delete a lead.

        Args:
            lead_id: Unique identifier of the lead

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_leads_by_branch(self, branch_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get all leads for a gym with optional filters.

        Args:
            branch_id: Unique identifier of the branch
            filters: Optional dictionary of filter criteria

        Returns:
            List of lead data matching the criteria
        """
        pass

    @abstractmethod
    async def get_leads_by_qualification(self, gym_id: str, qualification: str) -> List[Dict[str, Any]]:
        """
        Get leads by qualification status.

        Args:
            gym_id: Unique identifier of the gym
            qualification: Qualification status to filter by

        Returns:
            List of lead data with the specified qualification
        """
        pass

    @abstractmethod
    async def update_lead_qualification(self, lead_id: str, qualification: str) -> Optional[Dict[str, Any]]:
        """
        Update lead qualification status.

        Args:
            lead_id: Unique identifier of the lead
            qualification: New qualification status

        Returns:
            Updated lead data if successful, None if lead not found
        """
        pass

    @abstractmethod
    async def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Optional[Dict[str, Any]]:
        """
        Add tags to a lead.

        Args:
            lead_id: Unique identifier of the lead
            tags: List of tags to add

        Returns:
            Updated lead data if successful, None if lead not found
        """
        pass

    @abstractmethod
    async def remove_tags_from_lead(self, lead_id: str, tags: List[str]) -> Optional[Dict[str, Any]]:
        """
        Remove tags from a lead.

        Args:
            lead_id: Unique identifier of the lead
            tags: List of tags to remove

        Returns:
            Updated lead data if successful, None if lead not found
        """
        pass

    @abstractmethod
    async def update_lead_after_call(self, lead_id: str, call_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update lead information after a call.

        Args:
            lead_id: Unique identifier of the lead
            call_data: Dictionary containing call-related updates

        Returns:
            Updated lead data if successful, None if lead not found
        """
        pass

    @abstractmethod
    async def get_prioritized_leads(
        self, 
        branch_id: str, 
        count: int, 
        qualification: Optional[str] = None,
        exclude_leads: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get prioritized leads for campaigns.

        Args:
            branch_id: Unique identifier of the branch
            count: Number of leads to return
            qualification: Optional qualification status to filter by
            exclude_leads: Optional list of lead IDs to exclude

        Returns:
            List of prioritized lead data
        """
        pass

    @abstractmethod
    async def get_lead_call_history(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Get call history for a lead.

        Args:
            lead_id: Unique identifier of the lead

        Returns:
            List of call data associated with the lead
        """
        pass

    @abstractmethod
    async def update_lead_notes(self, lead_id: str, notes: str) -> Optional[Dict[str, Any]]:
        """
        Update lead notes.

        Args:
            lead_id: Unique identifier of the lead
            notes: New notes content

        Returns:
            Updated lead data if successful, None if lead not found
        """
        pass

    @abstractmethod
    async def get_leads_by_status(self, gym_id: str, status: str) -> List[Dict[str, Any]]:
        """
        Get leads by status.

        Args:
            gym_id: Unique identifier of the gym
            status: Status to filter by

        Returns:
            List of lead data with the specified status
        """
        pass

    @abstractmethod
    async def update_lead_status(self, lead_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update lead status.

        Args:
            lead_id: Unique identifier of the lead
            status: New status

        Returns:
            Updated lead data if successful, None if lead not found
        """
        pass

    @abstractmethod
    async def get_leads_for_retry(self, campaign_id: str, gap_days: int) -> List[Dict[str, Any]]:
        """
        Get leads eligible for retry calls.

        Args:
            campaign_id: Unique identifier of the campaign
            gap_days: Minimum days since last call

        Returns:
            List of lead data eligible for retry
        """
        pass 