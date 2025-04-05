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
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new lead.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Dictionary containing the created lead details
        """
        # Set created_at and updated_at timestamps if not provided
        if "created_at" not in lead_data:
            lead_data["created_at"] = datetime.now()
        if "updated_at" not in lead_data:
            lead_data["updated_at"] = datetime.now()
        
        # Create lead
        lead = await self.lead_repository.create_lead(lead_data)
        
        # Process tags if provided
        if tags := lead_data.get("tags"):
            await self.lead_repository.add_tags_to_lead(str(lead["id"]), tags)
            # Fetch updated lead with tags
            lead = await self.lead_repository.get_lead_by_id(str(lead["id"]))
        
        logger.info(f"Created new lead: {lead.get('id')}")
        return lead
    
    #correct parameters
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
    
    #Foreground Task
    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update lead information. When the user wants to through the user interface
        
        Args:
            lead_id: ID of the lead to update
            lead_data: Dictionary containing updated lead information
            
        Returns:
            Dictionary containing the updated lead details
        """
        # For immediate lightweight response
        
        # Otherwise, perform the update synchronously
        # Set updated_at timestamp
        lead_data["updated_at"] = datetime.now()
        
        # Map "status" field to "lead_status" field expected by the database model
        if "status" in lead_data:
            lead_data["lead_status"] = lead_data.pop("status")
        
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
            branch_id=gym_id,
            count=count,
            qualification=qualification,
            exclude_leads=exclude_leads
        )
        
        logger.info(f"Retrieved {len(leads)} prioritized leads for gym: {gym_id}")
        return leads
    
    #Background Task -> Purely a background task, after the call is made, we need to take that information and update the lead.
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
        # For immediate lightweight response
        if call_data.get("use_background_task", False):
            # Import here to avoid circular imports
            from ...tasks.lead.task_definitions import update_lead_after_call as update_lead_after_call_task
            
            # Remove the flag to avoid recursion or persistence in the data
            call_data.pop("use_background_task", None)
            
            # Queue the task for background processing
            update_lead_after_call_task.delay(lead_id, call_data)
            
            # Return minimal information immediately
            return {"id": lead_id, "status": "update_after_call_queued"}
        
        # Otherwise, perform the update synchronously
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
        # For immediate lightweight response when explicitly requested
        if isinstance(qualification, dict) and qualification.get("use_background_task", False):
            # Extract the actual qualification value
            qual_value = qualification.get("value")
            
            # Import here to avoid circular imports
            from ...tasks.lead.task_definitions import qualify_lead as qualify_lead_task
            
            # Queue the task for background processing
            qualify_lead_task.delay(lead_id, qual_value)
            
            # Return minimal information immediately
            return {"id": lead_id, "status": "qualification_queued"}
        
        # Otherwise, process qualification synchronously
        # Validate qualification
        valid_qualifications = ["hot", "cold", "neutral"]
        
        # Handle the case where qualification might be a dict from above logic
        qual_value = qualification.get("value") if isinstance(qualification, dict) else qualification
        
        if qual_value not in valid_qualifications:
            raise ValueError(f"Invalid qualification: {qual_value}. Must be one of {valid_qualifications}")
        
        # Update qualification
        lead = await self.lead_repository.update_lead_qualification(lead_id, qual_value)
        
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        logger.info(f"Updated lead qualification: {lead_id} -> {qual_value}")
        return lead
    
    #Manually Adding Tag -> Foreground Task, Automatically Adding Tag -> Background Task 
    async def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Add tags to a lead.
        
        Args:
            lead_id: ID of the lead
            tags: List of tags to add
            
        Returns:
            Dictionary containing the updated lead details
        """
        # For immediate lightweight response
        # Check if tags is actually a dict with use_background_task flag
        if isinstance(tags, dict) and tags.get("use_background_task", False):
            # Extract the actual tags
            tag_list = tags.get("values", [])
            
            # Import here to avoid circular imports
            from ...tasks.lead.task_definitions import add_tags_to_lead as add_tags_task
            
            # Queue the task for background processing
            add_tags_task.delay(lead_id, tag_list)
            
            # Return minimal information immediately
            return {"id": lead_id, "status": "add_tags_queued"}
        
        # Otherwise, process tags synchronously
        # Validate tags, handling the case where tags might be a dict from above logic
        tag_list = tags.get("values", []) if isinstance(tags, dict) else tags
        
        if not tag_list:
            return await self.get_lead(lead_id)
        
        # Add tags
        lead = await self.lead_repository.add_tags_to_lead(lead_id, tag_list)
        
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        logger.info(f"Added tags to lead: {lead_id} -> {tag_list}")
        return lead
    
    async def get_leads_by_status(self, branch_id: str, status: str) -> List[Dict[str, Any]]:
        """
        Get leads by status.
        
        Args:
            branch_id: ID of the branch (not gym_id)
            status: Status to filter by
            
        Returns:
            List of leads with the specified status
        """
        leads = await self.lead_repository.get_leads_by_status(branch_id, status)
        
        logger.info(f"Retrieved {len(leads)} leads with status '{status}' for branch: {branch_id}")
        return leads
    
    async def remove_tags_from_lead(self, lead_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Remove tags from a lead.
        
        Args:
            lead_id: ID of the lead
            tags: List of tag IDs to remove
            
        Returns:
            Dictionary containing the updated lead details
        """
        # Check if lead exists
        lead = await self.lead_repository.get_lead_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        # Remove tags
        lead = await self.lead_repository.remove_tags_from_lead(lead_id, tags)
        
        if not lead:
            raise ValueError(f"Failed to remove tags from lead: {lead_id}")
        
        logger.info(f"Removed tags from lead: {lead_id} -> {tags}")
        return lead
    
    async def delete_lead(self, lead_id: str) -> None:
        """
        Delete a lead by ID.
        
        Args:
            lead_id: ID of the lead to delete
            
        Returns:
            None
        
        Raises:
            ValueError: If lead not found
        """
        # Check if lead exists
        lead = await self.lead_repository.get_lead_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        # First, let's delete any related records to avoid foreign key constraint violations
        from sqlalchemy import delete, text
        from backend.db.connections.database import get_db_session
        
        try:
            # Get a session directly rather than using the context manager
            session = await get_db_session()
            
            try:
                # 1. Delete related members (must be first since it references the lead)
                delete_members_stmt = text("DELETE FROM members WHERE lead_id = :lead_id")
                await session.execute(delete_members_stmt, {"lead_id": lead_id})
                await session.commit()
                logger.info(f"Deleted members for lead: {lead_id}")
                
                # 2. Delete related appointments
                delete_appointments_stmt = text("DELETE FROM appointments WHERE lead_id = :lead_id")
                await session.execute(delete_appointments_stmt, {"lead_id": lead_id})
                await session.commit()
                logger.info(f"Deleted appointments for lead: {lead_id}")
                
                # 3. Delete related call logs
                delete_call_logs_stmt = text("DELETE FROM call_logs WHERE lead_id = :lead_id")
                await session.execute(delete_call_logs_stmt, {"lead_id": lead_id})
                await session.commit()
                logger.info(f"Deleted call logs for lead: {lead_id}")
                
                # 4. Delete related follow-up calls
                delete_follow_up_calls_stmt = text("DELETE FROM follow_up_calls WHERE lead_id = :lead_id")
                await session.execute(delete_follow_up_calls_stmt, {"lead_id": lead_id})
                await session.commit()
                logger.info(f"Deleted follow-up calls for lead: {lead_id}")
                
                # 5. Delete related lead tags
                delete_lead_tags_stmt = text("DELETE FROM lead_tag WHERE lead_id = :lead_id")
                await session.execute(delete_lead_tags_stmt, {"lead_id": lead_id})
                await session.commit()
                logger.info(f"Deleted tags for lead: {lead_id}")
                
                # 6. Finally, delete the lead itself
                await self.lead_repository.delete_lead(lead_id)
                logger.info(f"Deleted lead: {lead_id}")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting lead {lead_id}: {str(e)}")
                raise ValueError(f"Failed to delete lead: {str(e)}")
            finally:
                await session.close()
        except Exception as e:
            logger.error(f"Error obtaining database session: {str(e)}")
            raise ValueError(f"Failed to delete lead: {str(e)}")
    
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
            branch_id: ID of the branch
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
    
    async def remove_tags_from_lead(self, lead_id: str, tag_ids: List[str]) -> Dict[str, Any]:
        """
        Remove tags from a lead.
        
        Args:
            lead_id: ID of the lead
            tag_ids: List of tag IDs to remove
            
        Returns:
            Dictionary containing the updated lead details
        """
        # For immediate lightweight response
        # Check if tag_ids is actually a dict with use_background_task flag
        if isinstance(tag_ids, dict) and tag_ids.get("use_background_task", False):
            # Extract the actual tag IDs
            tag_list = tag_ids.get("values", [])
            
            # Import here to avoid circular imports
            from ...tasks.lead.task_definitions import remove_tags_from_lead as remove_tags_task
            
            # Queue the task for background processing
            remove_tags_task.delay(lead_id, tag_list)
            
            # Return minimal information immediately
            return {"id": lead_id, "status": "remove_tags_queued"}
        
        # Otherwise, process tag removal synchronously
        # Validate tag_ids, handling the case where tag_ids might be a dict from above logic
        tag_list = tag_ids.get("values", []) if isinstance(tag_ids, dict) else tag_ids
        
        if not tag_list:
            return await self.get_lead(lead_id)
        
        # Remove tags
        lead = await self.lead_repository.remove_tags_from_lead(lead_id, tag_list)
        
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        logger.info(f"Removed tags from lead: {lead_id} -> {tag_list}")
        return lead
