"""
Analytics repository interface defining the contract for analytics operations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class AnalyticsRepository(ABC):
    """
    Abstract base class defining the interface for analytics repository operations.
    Any concrete implementation must implement all these methods.
    """
    
    @abstractmethod
    async def save_daily_metrics(self, gym_id: str, date: datetime, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save daily metrics for a gym.

        Args:
            gym_id: Unique identifier of the gym
            date: The date for which metrics are being saved
            metrics: Dictionary containing metric data

        Returns:
            Dict containing the saved metrics data
        """
        pass

    @abstractmethod
    async def get_daily_metrics(self, gym_id: str, date: datetime) -> Optional[Dict[str, Any]]:
        """
        Get daily metrics for a gym.

        Args:
            gym_id: Unique identifier of the gym
            date: The date for which to retrieve metrics

        Returns:
            Metrics data if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_metrics_by_date_range(
        self,
        gym_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get metrics for a date range.

        Args:
            gym_id: Unique identifier of the gym
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            List of metrics data for each day in the range
        """
        pass

    @abstractmethod
    async def save_campaign_metrics(self, campaign_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save metrics for a campaign.

        Args:
            campaign_id: Unique identifier of the campaign
            metrics: Dictionary containing metric data

        Returns:
            Dict containing the saved metrics data
        """
        pass

    @abstractmethod
    async def get_campaign_metrics(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a campaign.

        Args:
            campaign_id: Unique identifier of the campaign

        Returns:
            Metrics data if found, None otherwise
        """
        pass

    @abstractmethod
    async def save_lead_qualification_metrics(
        self,
        gym_id: str,
        date: datetime,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save lead qualification metrics.

        Args:
            gym_id: Unique identifier of the gym
            date: The date for which metrics are being saved
            metrics: Dictionary containing qualification metrics

        Returns:
            Dict containing the saved metrics data
        """
        pass

    @abstractmethod
    async def get_lead_qualification_metrics(
        self,
        gym_id: str,
        date: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Get lead qualification metrics.

        Args:
            gym_id: Unique identifier of the gym
            date: The date for which to retrieve metrics

        Returns:
            Qualification metrics data if found, None otherwise
        """
        pass

    @abstractmethod
    async def save_call_outcome_metrics(
        self,
        gym_id: str,
        date: datetime,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save call outcome metrics.

        Args:
            gym_id: Unique identifier of the gym
            date: The date for which metrics are being saved
            metrics: Dictionary containing call outcome metrics

        Returns:
            Dict containing the saved metrics data
        """
        pass

    @abstractmethod
    async def get_call_outcome_metrics(
        self,
        gym_id: str,
        date: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Get call outcome metrics.

        Args:
            gym_id: Unique identifier of the gym
            date: The date for which to retrieve metrics

        Returns:
            Call outcome metrics data if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_call_volume_metrics(
        self,
        gym_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, List[int]]:
        """
        Get call volume metrics by day.

        Args:
            gym_id: Unique identifier of the gym
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            Dictionary mapping dates to call volumes
        """
        pass

    @abstractmethod
    async def save_sentiment_analysis(self, call_id: str, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save sentiment analysis results for a call.

        Args:
            call_id: Unique identifier of the call
            sentiment_data: Dictionary containing sentiment analysis results

        Returns:
            Dict containing the saved sentiment data
        """
        pass

    @abstractmethod
    async def get_sentiment_metrics(
        self,
        gym_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get sentiment metrics for a period.

        Args:
            gym_id: Unique identifier of the gym
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            Dictionary containing aggregated sentiment metrics
        """
        pass

    @abstractmethod
    async def save_conversion_metrics(
        self,
        gym_id: str,
        date: datetime,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save conversion metrics.

        Args:
            gym_id: Unique identifier of the gym
            date: The date for which metrics are being saved
            metrics: Dictionary containing conversion metrics

        Returns:
            Dict containing the saved metrics data
        """
        pass

    @abstractmethod
    async def get_conversion_metrics(
        self,
        gym_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get conversion metrics for a period.

        Args:
            gym_id: Unique identifier of the gym
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            List of conversion metrics data for the period
        """
        pass 