"""
Interface for the Campaign Management Service.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class CampaignService(ABC):
    """
    Interface for the Campaign Management Service.
    """
    
    @abstractmethod
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call campaign.
        
        Args:
            campaign_data: Dictionary containing campaign configuration
                - start_date: Start date for the campaign
                - end_date: End date for the campaign
                - frequency: Maximum calls per day
                - lead_qualification: Qualification criteria for leads (hot, cold, neutral)
                - gym_id: ID of the gym
                - max_call_duration: Maximum call duration in seconds
                - call_days: List of days to make calls (mon, tue, wed, etc.)
                - retry_number: Number of retry attempts
                - gap: Gap between retries in days
                
        Returns:
            Dictionary containing the created campaign details
        """
        pass
    
    @abstractmethod
    async def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign details by ID.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary containing campaign details
        """
        pass
    
    @abstractmethod
    async def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing campaign.
        
        Args:
            campaign_id: ID of the campaign to update
            campaign_data: Dictionary containing updated campaign configuration
            
        Returns:
            Dictionary containing the updated campaign details
        """
        pass
    
    @abstractmethod
    async def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete a campaign.
        
        Args:
            campaign_id: ID of the campaign to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def schedule_calls(self, campaign_id: str, date: datetime) -> List[Dict[str, Any]]:
        """
        Schedule calls for a specific date based on campaign configuration.
        
        Args:
            campaign_id: ID of the campaign
            date: Date to schedule calls for
            
        Returns:
            List of scheduled calls
        """
        pass
    
    @abstractmethod
    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get metrics for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary containing campaign metrics
        """
        pass
    
    @abstractmethod
    async def list_campaigns(self, gym_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List campaigns for a gym with optional filtering.
        
        Args:
            gym_id: ID of the gym
            filters: Optional filters for the campaigns
            
        Returns:
            List of campaigns matching the criteria
        """
        pass

    @abstractmethod
    async def increment_call_count(self, campaign_id: str, count: int = 1) -> Dict[str, Any]:
        """
        Increment the call count for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            count: Number to increment by (default 1)
            
        Returns:
            Updated campaign data
        """
        pass