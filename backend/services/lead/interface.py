"""
Interface for the Lead Management Service.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LeadService(ABC):
    """
    Interface for the Lead Management Service.
    """
    
    @abstractmethod
    async def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Get lead details by ID.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            Dictionary containing lead details
        """
        pass
    
    @abstractmethod
    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update lead information.
        
        Args:
            lead_id: ID of the lead to update
            lead_data: Dictionary containing updated lead information
            
        Returns:
            Dictionary containing the updated lead details
        """
        pass
    
    @abstractmethod
    async def get_prioritized_leads(
        self, 
        gym_id: str, 
        count: int, 
        qualification: Optional[str] = None,
        exclude_leads: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get prioritized leads for a gym based on qualification criteria.
        
        Args:
            gym_id: ID of the gym
            count: Number of leads to return
            qualification: Optional qualification filter (hot, cold, neutral)
            exclude_leads: Optional list of lead IDs to exclude
            
        Returns:
            List of prioritized leads
        """
        pass
    
    @abstractmethod
    async def update_lead_after_call(self, lead_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update lead information after a call.
        
        Args:
            lead_id: ID of the lead
            call_data: Dictionary containing call information
                - call_id: ID of the call
                - outcome: Outcome of the call
                - notes: Notes from the call
                - tags: Tags to add to the lead
                - qualification: Updated qualification status
                - sentiment: Sentiment analysis result
                
        Returns:
            Dictionary containing the updated lead details
        """
        pass
    
    @abstractmethod
    async def qualify_lead(self, lead_id: str, qualification: str) -> Dict[str, Any]:
        """
        Update lead qualification status.
        
        Args:
            lead_id: ID of the lead
            qualification: Qualification status (hot, cold, neutral)
            
        Returns:
            Dictionary containing the updated lead details
        """
        pass
    
    @abstractmethod
    async def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Add tags to a lead.
        
        Args:
            lead_id: ID of the lead
            tags: List of tags to add
            
        Returns:
            Dictionary containing the updated lead details
        """
        pass
    
    @abstractmethod
    async def get_leads_by_status(self, gym_id: str, status: str) -> List[Dict[str, Any]]:
        """
        Get leads by status.
        
        Args:
            gym_id: ID of the gym
            status: Status to filter by
            
        Returns:
            List of leads with the specified status
        """
        pass
    
    @abstractmethod
    async def get_paginated_leads(
        self,
        gym_id: str,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get paginated leads for a gym with optional filters.
        
        Args:
            gym_id: ID of the gym
            page: Page number (1-based)
            page_size: Number of leads per page
            filters: Optional dictionary of filter criteria
            
        Returns:
            Dictionary containing:
                - leads: List of lead data
                - pagination: Dictionary with total, page, page_size, and pages
        """
        pass 