"""
PostgreSQL implementation of the LeadRepository interface.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from ....models.lead import Lead
from ....models.lead.lead_tag import lead_tag
from ....models.lead.tag import Tag
from ....models.call.call_log import CallLog
from ....models.campaign.follow_up_campaign import FollowUpCampaign
from ...lead.interface import LeadRepository
from ....helpers.lead.lead_queries import (
    get_lead_with_related_data,
    update_lead_db,
    build_lead_filters,
    get_leads_by_gym_with_filters,
    update_lead_after_call_db,
    get_prioritized_leads_db,
    get_leads_for_retry_db
)
from .....utils.logging.logger import get_logger

logger = get_logger(__name__)

class PostgresLeadRepository(LeadRepository):
    """PostgreSQL implementation of the LeadRepository interface."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with a database session."""
        self.session = session
    
    #Works - Add error handling
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead."""
        # Create lead record
        lead = Lead(**lead_data)
        self.session.add(lead)
        await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead.id)
    
    #Works
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get lead details by ID."""
        return await get_lead_with_related_data(self.session, lead_id)
    
    #Works
    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update lead details."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return None
        
        # Update lead record
        update_query = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(**lead_data)
        )
        await self.session.execute(update_query)
        await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead_id)
    #Works
    async def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return False
        
        # Delete lead record
        delete_query = delete(Lead).where(Lead.id == lead_id)
        await self.session.execute(delete_query)
        await self.session.commit()
        
        return True
    
    #Works
    async def get_leads_by_branch(
        self,
        branch_id: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get all leads for a gym with optional filters."""
        return await get_leads_by_gym_with_filters(
            self.session,
            branch_id,
            filters,
            page,
            page_size
        )
    
    #Ignore
    async def get_leads_by_qualification(
        self,
        gym_id: str,
        qualification: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get leads by qualification status."""
        filters = {"qualification": qualification}
        return await get_leads_by_gym_with_filters(
            self.session,
            gym_id,
            filters,
            page,
            page_size
        )
    
    #Ignore
    async def update_lead_qualification(
        self,
        lead_id: str,
        qualification: str
    ) -> Optional[Dict[str, Any]]:
        """Update the qualification status of a lead."""
        # Check if lead exists
        return await update_lead_db(self.session, lead_id, {"qualification_score": qualification})
    
    #Works
    async def add_tags_to_lead(
        self,
        lead_id: str,
        tags: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Add tags to a lead."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return None
        
        # Get existing tags for this lead
        existing_tags_query = (
            select(Tag)
            .join(lead_tag, Tag.id == lead_tag.c.tag_id)
            .where(lead_tag.c.lead_id == lead_id)
        )
        existing_tags_result = await self.session.execute(existing_tags_query)
        existing_tags = existing_tags_result.scalars().all()
        existing_tag_names = [tag.name for tag in existing_tags]
        
        # Add only new tags
        for tag_name in tags:
            if tag_name not in existing_tag_names:
                # Check if tag exists
                tag_query = select(Tag).where(Tag.name == tag_name)
                tag_result = await self.session.execute(tag_query)
                tag = tag_result.scalar_one_or_none()
                
                if not tag:
                    # Create new tag
                    tag = Tag(name=tag_name)
                    self.session.add(tag)
                    await self.session.flush()  # Flush to get the ID
                
                # Create association
                stmt = insert(lead_tag).values(
                    lead_id=lead_id,
                    tag_id=tag.id,
                    created_at=datetime.now()
                )
                await self.session.execute(stmt)
        
        await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead_id)
    
    #Works
    async def remove_tags_from_lead(
        self,
        lead_id: str,
        tags: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Remove tags from a lead."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return None
        
        # Get tag IDs to remove
        tag_ids_query = select(Tag.id).where(Tag.name.in_(tags))
        tag_ids_result = await self.session.execute(tag_ids_query)
        tag_ids = [row[0] for row in tag_ids_result]
        
        if tag_ids:
            # Delete specified tag associations
            delete_query = delete(lead_tag).where(and_(
                lead_tag.c.lead_id == lead_id,
                lead_tag.c.tag_id.in_(tag_ids)
            ))
            await self.session.execute(delete_query)
            await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead_id)
    
    #Doesn't work because of agent_user_id -> Needs fixing.
    async def update_lead_after_call(
        self,
        lead_id: str,
        call_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update lead information after a call."""
        return await update_lead_after_call_db(self.session, lead_id, call_data)
    
    async def get_lead_call_history(
        self,
        lead_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get call history for a lead."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return {
                "calls": [],
                "pagination": {
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "pages": 0
                }
            }
        
        # Count total calls
        count_query = select(func.count()).select_from(
            select(CallLog).where(CallLog.lead_id == lead_id).subquery()
        )
        total_count = await self.session.execute(count_query)
        total = total_count.scalar_one()
        
        # Get calls with pagination
        offset = (page - 1) * page_size
        calls_query = (
            select(CallLog)
            .where(CallLog.lead_id == lead_id)
            .order_by(desc(CallLog.created_at))
            .offset(offset)
            .limit(page_size)
        )
        calls_result = await self.session.execute(calls_query)
        calls = calls_result.scalars().all()
        
        return {
            "calls": [call.to_dict() for call in calls],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        }
    
    #Works
    async def get_prioritized_leads(
        self,
        branch_id: str,
        count: int,
        qualification: Optional[str] = None,
        exclude_leads: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get prioritized leads for campaigns."""
        return await get_prioritized_leads_db(
            self.session,
            branch_id,
            count,
            qualification,
            exclude_leads
        )
    
    async def get_leads_for_retry(
        self,
        campaign_id: str,
        gap_days: int
    ) -> List[Dict[str, Any]]:
        """Get leads eligible for retry calls."""
        return await get_leads_for_retry_db(self.session, campaign_id, gap_days) 
    

    async def update_lead_notes(self, lead_id: str, notes: str) -> Optional[Dict[str, Any]]:
        """
        Update lead notes.

        Args:
            lead_id: Unique identifier of the lead
            notes: New notes content

        Returns:
            Updated lead data if successful, None if lead not found
        """
        # Check if lead exists
        return await update_lead_db(self.session, lead_id, {"notes": notes})

    #Works
    async def get_leads_by_status(self, branch_id: str, status: str) -> List[Dict[str, Any]]:
        """
        Get leads by status.

        Args:
            branch_id: Unique identifier of the branch
            status: Status to filter by

        Returns:
            List of lead data with the specified status
        """
        filters = {"lead_status": status}
        results = await get_leads_by_gym_with_filters(
            self.session,
            branch_id,
            filters,
            page=1,
            page_size=100
        )
        return results.get("leads", [])

    #Works
    async def update_lead_status(self, lead_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update lead status.

        Args:
            lead_id: Unique identifier of the lead
            status: New status

        Returns:
            Updated lead data if successful, None if lead not found
        """
        # Check if lead exists
        return await update_lead_db(self.session, lead_id, {"lead_status": status})
