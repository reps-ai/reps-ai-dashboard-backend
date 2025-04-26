"""
Analytics repository interface defining data access methods for analytics.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class AnalyticsRepository(ABC):
    """Interface for the Analytics Repository."""
    
    @abstractmethod
    async def store_lead_performance_metrics(
        self,
        branch_id: str,
        metrics_data: Dict[str, Any],
        period_type: str,
        target_date: datetime
    ) -> Dict[str, Any]:
        """
        Store lead performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            metrics_data: Dictionary containing lead metrics data
            period_type: Type of period ("daily", "weekly", "monthly")
            target_date: Target date for the metrics
            
        Returns:
            Stored metrics data
        """
        pass
    
    @abstractmethod
    async def store_call_performance_metrics(
        self,
        branch_id: str,
        metrics_data: Dict[str, Any],
        period_type: str,
        target_date: datetime
    ) -> Dict[str, Any]:
        """
        Store call performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            metrics_data: Dictionary containing call metrics data
            period_type: Type of period ("daily", "weekly", "monthly")
            target_date: Target date for the metrics
            
        Returns:
            Stored metrics data
        """
        pass
    
    @abstractmethod
    async def get_lead_performance_metrics(
        self,
        branch_id: str,
        period_type: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get lead performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            period_type: Type of period ("daily", "weekly", "monthly")
            start_date: Start date for the metrics
            end_date: Optional end date for the metrics
            
        Returns:
            List of lead performance metrics
        """
        pass
    
    @abstractmethod
    async def get_call_performance_metrics(
        self,
        branch_id: str,
        period_type: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get call performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            period_type: Type of period ("daily", "weekly", "monthly")
            start_date: Start date for the metrics
            end_date: Optional end date for the metrics
            
        Returns:
            List of call performance metrics
        """
        pass
    
    @abstractmethod
    async def get_latest_lead_performance_metrics(
        self,
        branch_id: str,
        period_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest lead performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            period_type: Type of period ("daily", "weekly", "monthly")
            
        Returns:
            Latest lead performance metrics or None if not found
        """
        pass
    
    @abstractmethod
    async def get_latest_call_performance_metrics(
        self,
        branch_id: str,
        period_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest call performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            period_type: Type of period ("daily", "weekly", "monthly")
            
        Returns:
            Latest call performance metrics or None if not found
        """
        pass
    
    @abstractmethod
    async def get_time_of_day_performance(
        self,
        branch_id: str,
        target_date: datetime
    ) -> Dict[str, Any]:
        """
        Get time-of-day performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            target_date: Target date for the metrics
            
        Returns:
            Time-of-day performance metrics
        """
        pass
    
    @abstractmethod
    async def get_customer_journey_metrics(
        self,
        branch_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get customer journey metrics for a branch.
        
        Args:
            branch_id: Branch ID
            start_date: Start date for the metrics
            end_date: End date for the metrics
            
        Returns:
            Customer journey metrics
        """
        pass
    
    @abstractmethod
    async def get_staff_performance(
        self,
        branch_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get staff performance metrics for a branch.
        
        Args:
            branch_id: Branch ID
            start_date: Start date for the metrics
            end_date: End date for the metrics
            
        Returns:
            Staff performance metrics
        """
        pass
