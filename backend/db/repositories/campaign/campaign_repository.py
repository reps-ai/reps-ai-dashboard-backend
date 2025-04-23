"""
Campaign repository interface defining the contract for campaign operations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date

class CampaignRepository(ABC):
    """
    Abstract base class defining the interface for campaign repository operations.
    Any concrete implementation must implement all these methods.
    """
    
    @abstractmethod
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new campaign.

        Args:
            campaign_data: Dictionary containing campaign details

        Returns:
            Dict containing the created campaign data
        """
        pass

    @abstractmethod
    async def get_campaign_by_id(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get campaign details by ID.

        Args:
            campaign_id: Unique identifier of the campaign

        Returns:
            Campaign data if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update campaign details.

        Args:
            campaign_id: Unique identifier of the campaign
            campaign_data: Dictionary containing updated campaign details

        Returns:
            Updated campaign data if successful, None if campaign not found
        """
        pass

    @abstractmethod
    async def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete a campaign.

        Args:
            campaign_id: Unique identifier of the campaign

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_active_campaigns(self, gym_id: str) -> List[Dict[str, Any]]:
        """
        Get all active campaigns for a gym.

        Args:
            gym_id: Unique identifier of the gym

        Returns:
            List of active campaign data
        """
        pass

    @abstractmethod
    async def get_campaigns_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """
        Get campaigns scheduled for a specific date.

        Args:
            target_date: The date to get campaigns for

        Returns:
            List of campaign data scheduled for the date
        """
        pass

    @abstractmethod
    async def update_campaign_metrics(self, campaign_id: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update campaign metrics.

        Args:
            campaign_id: Unique identifier of the campaign
            metrics: Dictionary containing metric updates

        Returns:
            Updated campaign data if successful, None if campaign not found
        """
        pass

    @abstractmethod
    async def get_campaign_leads(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Get all leads associated with a campaign.

        Args:
            campaign_id: Unique identifier of the campaign

        Returns:
            List of lead data associated with the campaign
        """
        pass

    @abstractmethod
    async def add_leads_to_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """
        Add leads to a campaign.

        Args:
            campaign_id: Unique identifier of the campaign
            lead_ids: List of lead IDs to add

        Returns:
            True if leads were added successfully, False otherwise
        """
        pass

    @abstractmethod
    async def remove_leads_from_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """
        Remove leads from a campaign.

        Args:
            campaign_id: Unique identifier of the campaign
            lead_ids: List of lead IDs to remove

        Returns:
            True if leads were removed successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_campaign_schedule(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get the calling schedule for a campaign.

        Args:
            campaign_id: Unique identifier of the campaign

        Returns:
            Dictionary containing schedule details
        """
        pass

    @abstractmethod
    async def update_campaign_schedule(self, campaign_id: str, schedule_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update the calling schedule for a campaign.

        Args:
            campaign_id: Unique identifier of the campaign
            schedule_data: Dictionary containing updated schedule details

        Returns:
            Updated schedule data if successful, None if campaign not found
        """
        pass

    @abstractmethod
    async def get_call_ids_for_campaign(self, campaign_id: str) -> List[str]:
        """
        Get IDs of all calls associated with a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            List of call IDs
        """
        pass