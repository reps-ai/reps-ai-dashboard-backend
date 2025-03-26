"""
Implementation of the Lead Management Service.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from .interface import LeadService
from ...db.repositories.lead import LeadRepository
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

class DefaultLeadService(LeadService):
    """
    Default implementation of the Lead Management Service.
    """
    
    """Vishwas Implements"""
    def __init__(self, lead_repository: LeadRepository):
        """
        Initialize the lead service.
        
        Args:
            lead_repository: Repository for lead operations
        """
        self.lead_repository = lead_repository
    
    async def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Get lead details by ID.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            Dictionary containing lead details
        """
        lead = await self.lead_repository.get_lead_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        return lead
    
    #Background Task
    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update lead information.
        
        Args:
            lead_id: ID of the lead to update
            lead_data: Dictionary containing updated lead information
            
        Returns:
            Dictionary containing the updated lead details
        """
        # Set updated_at timestamp
        lead_data["updated_at"] = datetime.now()
        
        # Update lead
        lead = await self.lead_repository.update_lead(lead_id, lead_data)
        
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        logger.info(f"Updated lead: {lead_id}")
        return lead
    
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
        leads = await self.lead_repository.get_prioritized_leads(
            gym_id=gym_id,
            count=count,
            qualification=qualification,
            exclude_leads=exclude_leads
        )
        
        logger.info(f"Retrieved {len(leads)} prioritized leads for gym: {gym_id}")
        return leads
    
    #Background Task
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
        # Validate call data
        if "call_id" not in call_data:
            raise ValueError("Call ID is required")
        
        # Process qualification if provided
        if qualification := call_data.get("qualification"):
            await self.qualify_lead(lead_id, qualification)
        
        # Process tags if provided
        if tags := call_data.get("tags"):
            await self.add_tags_to_lead(lead_id, tags)
        
        # Update lead with call information
        lead = await self.lead_repository.update_lead_after_call(lead_id, call_data)
        
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        logger.info(f"Updated lead after call: {lead_id}, call: {call_data.get('call_id')}")
        return lead
    
    #Background Task
    async def qualify_lead(self, lead_id: str, qualification: str) -> Dict[str, Any]:
        """
        Update lead qualification status.
        
        Args:
            lead_id: ID of the lead
            qualification: Qualification status (hot, cold, neutral)
            
        Returns:
            Dictionary containing the updated lead details
        """
        # Validate qualification
        valid_qualifications = ["hot", "cold", "neutral"]
        if qualification not in valid_qualifications:
            raise ValueError(f"Invalid qualification: {qualification}. Must be one of {valid_qualifications}")
        
        # Update qualification
        lead = await self.lead_repository.update_lead_qualification(lead_id, qualification)
        
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        logger.info(f"Updated lead qualification: {lead_id} -> {qualification}")
        return lead
    
    #Background Task
    async def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Add tags to a lead.
        
        Args:
            lead_id: ID of the lead
            tags: List of tags to add
            
        Returns:
            Dictionary containing the updated lead details
        """
        # Validate tags
        if not tags:
            return await self.get_lead(lead_id)
        
        # Add tags
        lead = await self.lead_repository.add_tags_to_lead(lead_id, tags)
        
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        logger.info(f"Added tags to lead: {lead_id} -> {tags}")
        return lead
    
    async def get_leads_by_status(self, gym_id: str, status: str) -> List[Dict[str, Any]]:
        """
        Get leads by status.
        
        Args:
            gym_id: ID of the gym
            status: Status to filter by
            
        Returns:
            List of leads with the specified status
        """
        leads = await self.lead_repository.get_leads_by_status(gym_id, status)
        
        logger.info(f"Retrieved {len(leads)} leads with status '{status}' for gym: {gym_id}")
        return leads
    
    async def get_paginated_leads(
        self,
        branch_id: str,
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
        result = await self.lead_repository.get_leads_by_branch(
            branch_id=branch_id,
            filters=filters,
            page=page,
            page_size=page_size
        )
        
        leads = result.get('leads', [])
        pagination = result.get('pagination', {})
        logger.info(
            f"Retrieved {len(leads)} leads for branch: {branch_id}, "
            f"page: {page}, total: {pagination.get('total', 0)}"
        )
        return result 