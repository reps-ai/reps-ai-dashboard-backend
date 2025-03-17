"""
PostgreSQL implementation of the LeadRepository interface.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from ....models.lead import Lead
from ....models.lead_tag import LeadTag
from ....models.lead_call import LeadCall
from ....models.lead_qualification import LeadQualification
from ....models.campaign_lead import CampaignLead
from ...lead.interface import LeadRepository
from ....helpers.lead.lead_queries import (
    get_lead_with_related_data,
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
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead."""
        # Create lead record
        lead = Lead(**lead_data)
        self.session.add(lead)
        await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead.id)
    
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get lead details by ID."""
        return await get_lead_with_related_data(self.session, lead_id)
    
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
    
    async def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return False
        
        # Delete lead record
        from sqlalchemy import delete
        delete_query = delete(Lead).where(Lead.id == lead_id)
        await self.session.execute(delete_query)
        await self.session.commit()
        
        return True
    
    async def get_leads_by_gym(
        self,
        gym_id: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get all leads for a gym with optional filters."""
        return await get_leads_by_gym_with_filters(
            self.session,
            gym_id,
            filters,
            page,
            page_size
        )
    
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
    
    async def update_lead_qualification(
        self,
        lead_id: str,
        qualification: str
    ) -> Optional[Dict[str, Any]]:
        """Update the qualification status of a lead."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return None
        
        # Set all current qualifications to not current
        update_query = (
            update(LeadQualification)
            .where(and_(
                LeadQualification.lead_id == lead_id,
                LeadQualification.is_current == True
            ))
            .values(is_current=False)
        )
        await self.session.execute(update_query)
        
        # Create new qualification record
        new_qualification = LeadQualification(
            lead_id=lead_id,
            qualification=qualification,
            is_current=True,
            created_at=datetime.now()
        )
        self.session.add(new_qualification)
        await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead_id)
    
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
        
        # Get existing tags
        existing_tags_query = select(LeadTag.tag).where(LeadTag.lead_id == lead_id)
        existing_tags_result = await self.session.execute(existing_tags_query)
        existing_tags = [row[0] for row in existing_tags_result]
        
        # Add only new tags
        new_tags = [tag for tag in tags if tag not in existing_tags]
        for tag in new_tags:
            lead_tag = LeadTag(lead_id=lead_id, tag=tag)
            self.session.add(lead_tag)
        
        await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead_id)
    
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
        
        # Delete specified tags
        from sqlalchemy import delete
        delete_query = (
            delete(LeadTag)
            .where(and_(
                LeadTag.lead_id == lead_id,
                LeadTag.tag.in_(tags)
            ))
        )
        await self.session.execute(delete_query)
        await self.session.commit()
        
        return await get_lead_with_related_data(self.session, lead_id)
    
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
            select(LeadCall).where(LeadCall.lead_id == lead_id).subquery()
        )
        total_count = await self.session.execute(count_query)
        total = total_count.scalar_one()
        
        # Get calls with pagination
        offset = (page - 1) * page_size
        calls_query = (
            select(LeadCall)
            .where(LeadCall.lead_id == lead_id)
            .order_by(desc(LeadCall.call_time))
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
    
    async def get_prioritized_leads(
        self,
        gym_id: str,
        count: int,
        qualification: Optional[str] = None,
        exclude_leads: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get prioritized leads for campaigns."""
        return await get_prioritized_leads_db(
            self.session,
            gym_id,
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