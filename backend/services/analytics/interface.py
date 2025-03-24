"""
Interface for the Analytics Service.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class AnalyticsService(ABC):
    """
    Interface for the Analytics Service.
    """
    
    @abstractmethod
    async def analyze_sentiment(self, transcript: List[Dict[str, Any]]) -> str:
        """
        Analyze sentiment in a call transcript.
        
        Args:
            transcript: List of transcript entries
            
        Returns:
            Sentiment result (positive, neutral, negative)
        """
        pass
    
    @abstractmethod
    async def calculate_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Calculate metrics for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary containing campaign metrics
        """
        pass
    
    @abstractmethod
    async def generate_dashboard_data(self, gym_id: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate data for dashboard display.
        
        Args:
            gym_id: ID of the gym
            date: Optional date for the data (defaults to today)
            
        Returns:
            Dictionary containing dashboard data
        """
        pass
    
    @abstractmethod
    async def get_call_metrics_by_date_range(
        self, 
        gym_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get call metrics for a gym within a date range.
        
        Args:
            gym_id: ID of the gym
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            Dictionary containing call metrics
        """
        pass
    
    @abstractmethod
    async def get_lead_qualification_distribution(self, gym_id: str) -> Dict[str, int]:
        """
        Get distribution of lead qualifications for a gym.
        
        Args:
            gym_id: ID of the gym
            
        Returns:
            Dictionary containing counts for each qualification level
        """
        pass
    
    @abstractmethod
    async def get_call_outcome_distribution(
        self, 
        gym_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        Get distribution of call outcomes for a gym.
        
        Args:
            gym_id: ID of the gym
            start_date: Optional start date for the range
            end_date: Optional end date for the range
            
        Returns:
            Dictionary containing counts for each outcome type
        """
        pass
    
    @abstractmethod
    async def get_call_volume_by_day(
        self, 
        gym_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, int]:
        """
        Get call volume by day for a gym.
        
        Args:
            gym_id: ID of the gym
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            Dictionary mapping dates to call counts
        """
        pass 