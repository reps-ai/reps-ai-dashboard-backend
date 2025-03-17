"""
PostgreSQL implementation of the lead repository.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, and_, or_, func, desc

from ..lead_repository import LeadRepository
from ....models.lead import Lead
from ....models.lead_tag import LeadTag
from ....models.lead_call import LeadCall
from ....models.lead_qualification import LeadQualification
from ....models.campaign_lead import CampaignLead
from .....tasks.lead.lead_processing import (
    get_leads_by_gym_with_filters,
    update_lead_after_call,
    get_prioritized_leads,
    get_leads_for_retry
)

class PostgresLeadRepository(LeadRepository):
    """
    PostgreSQL implementation of lead repository operations.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead."""
        # Extract tags if present
        tags = lead_data.pop("tags", []) if "tags" in lead_data else []
        
        # Create lead record
        lead = Lead(**lead_data)
        self.session.add(lead)
        await self.session.flush()
        
        # Add tags if provided
        if tags:
            await self._add_tags_to_lead(lead.id, tags)
        
        await self.session.commit()
        return await self._get_lead_with_related_data(lead.id)

    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get lead details by ID."""
        return await self._get_lead_with_related_data(lead_id)

    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update lead details."""
        # Extract tags if present
        tags = None
        if "tags" in lead_data:
            tags = lead_data.pop("tags")
        
        # Update lead record
        query = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(**lead_data)
            .returning(Lead)
        )
        result = await self.session.execute(query)
        lead = result.scalar_one_or_none()
        
        if not lead:
            return None
        
        # Update tags if provided
        if tags is not None:
            # Clear existing tags
            delete_query = delete(LeadTag).where(LeadTag.lead_id == lead_id)
            await self.session.execute(delete_query)
            
            # Add new tags
            if tags:
                await self._add_tags_to_lead(lead_id, tags)
        
        await self.session.commit()
        return await self._get_lead_with_related_data(lead_id)

    async def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""
        # Delete related records first
        tag_query = delete(LeadTag).where(LeadTag.lead_id == lead_id)
        await self.session.execute(tag_query)
        
        qual_query = delete(LeadQualification).where(LeadQualification.lead_id == lead_id)
        await self.session.execute(qual_query)
        
        campaign_query = delete(CampaignLead).where(CampaignLead.lead_id == lead_id)
        await self.session.execute(campaign_query)
        
        # Delete the lead
        query = delete(Lead).where(Lead.id == lead_id)
        result = await self.session.execute(query)
        await self.session.commit()
        
        return result.rowcount > 0

    async def get_leads_by_gym(self, gym_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all leads for a gym with optional filters."""
        # Use the task function for this complex operation
        result = await get_leads_by_gym_with_filters(
            session=self.session,
            gym_id=gym_id,
            filters=filters
        )
        return result["leads"]

    async def get_leads_by_qualification(self, gym_id: str, qualification: str) -> List[Dict[str, Any]]:
        """Get leads by qualification status."""
        query = (
            select(Lead)
            .join(LeadQualification)
            .where(and_(
                Lead.gym_id == gym_id,
                LeadQualification.qualification == qualification,
                LeadQualification.is_current == True
            ))
        )
        
        result = await self.session.execute(query)
        leads = result.scalars().all()
        
        return [await self._get_lead_with_related_data(lead.id) for lead in leads]

    async def update_lead_qualification(self, lead_id: str, qualification: str) -> Optional[Dict[str, Any]]:
        """Update lead qualification status."""
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
        return await self._get_lead_with_related_data(lead_id)

    async def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Optional[Dict[str, Any]]:
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
        if new_tags:
            await self._add_tags_to_lead(lead_id, new_tags)
            await self.session.commit()
        
        return await self._get_lead_with_related_data(lead_id)

    async def remove_tags_from_lead(self, lead_id: str, tags: List[str]) -> Optional[Dict[str, Any]]:
        """Remove tags from a lead."""
        # Check if lead exists
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return None
        
        # Delete specified tags
        delete_query = (
            delete(LeadTag)
            .where(and_(
                LeadTag.lead_id == lead_id,
                LeadTag.tag.in_(tags)
            ))
        )
        await self.session.execute(delete_query)
        await self.session.commit()
        
        return await self._get_lead_with_related_data(lead_id)

    async def update_lead_after_call(self, lead_id: str, call_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update lead information after a call."""
        # Use the task function for this complex operation
        return await update_lead_after_call(
            session=self.session,
            lead_id=lead_id,
            call_data=call_data
        )

    async def get_prioritized_leads(
        self, 
        gym_id: str, 
        count: int, 
        qualification: Optional[str] = None,
        exclude_leads: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get prioritized leads for campaigns."""
        # Use the task function for this complex operation
        return await get_prioritized_leads(
            session=self.session,
            gym_id=gym_id,
            count=count,
            qualification=qualification,
            exclude_leads=exclude_leads
        )

    async def get_lead_call_history(self, lead_id: str) -> List[Dict[str, Any]]:
        """Get call history for a lead."""
        query = (
            select(LeadCall)
            .where(LeadCall.lead_id == lead_id)
            .order_by(desc(LeadCall.call_time))
        )
        
        result = await self.session.execute(query)
        calls = result.scalars().all()
        
        return [call.to_dict() for call in calls]

    async def update_lead_notes(self, lead_id: str, notes: str) -> Optional[Dict[str, Any]]:
        """Update lead notes."""
        query = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(notes=notes)
            .returning(Lead)
        )
        
        result = await self.session.execute(query)
        lead = result.scalar_one_or_none()
        
        if not lead:
            return None
        
        await self.session.commit()
        return await self._get_lead_with_related_data(lead_id)

    async def get_leads_by_status(self, gym_id: str, status: str) -> List[Dict[str, Any]]:
        """Get leads by status."""
        query = (
            select(Lead)
            .where(and_(
                Lead.gym_id == gym_id,
                Lead.status == status
            ))
        )
        
        result = await self.session.execute(query)
        leads = result.scalars().all()
        
        return [await self._get_lead_with_related_data(lead.id) for lead in leads]

    async def update_lead_status(self, lead_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update lead status."""
        query = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(status=status)
            .returning(Lead)
        )
        
        result = await self.session.execute(query)
        lead = result.scalar_one_or_none()
        
        if not lead:
            return None
        
        await self.session.commit()
        return await self._get_lead_with_related_data(lead_id)

    async def get_leads_for_retry(self, campaign_id: str, gap_days: int) -> List[Dict[str, Any]]:
        """Get leads eligible for retry calls."""
        # Use the task function for this complex operation
        return await get_leads_for_retry(
            session=self.session,
            campaign_id=campaign_id,
            gap_days=gap_days
        )

    # Helper methods
    async def _get_lead_with_related_data(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get a lead with all related data."""
        # Get lead
        lead_query = select(Lead).where(Lead.id == lead_id)
        lead_result = await self.session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
        
        if not lead:
            return None
        
        lead_dict = lead.to_dict()
        
        # Get tags
        tags_query = select(LeadTag.tag).where(LeadTag.lead_id == lead_id)
        tags_result = await self.session.execute(tags_query)
        lead_dict["tags"] = [row[0] for row in tags_result]
        
        # Get current qualification
        qual_query = (
            select(LeadQualification)
            .where(and_(
                LeadQualification.lead_id == lead_id,
                LeadQualification.is_current == True
            ))
        )
        qual_result = await self.session.execute(qual_query)
        qualification = qual_result.scalar_one_or_none()
        lead_dict["qualification"] = qualification.qualification if qualification else None
        
        # Get last call
        call_query = (
            select(LeadCall)
            .where(LeadCall.lead_id == lead_id)
            .order_by(desc(LeadCall.call_time))
            .limit(1)
        )
        call_result = await self.session.execute(call_query)
        last_call = call_result.scalar_one_or_none()
        lead_dict["last_call"] = last_call.to_dict() if last_call else None
        
        return lead_dict

    async def _add_tags_to_lead(self, lead_id: str, tags: List[str]) -> None:
        """Add tags to a lead."""
        for tag in tags:
            lead_tag = LeadTag(lead_id=lead_id, tag=tag)
            self.session.add(lead_tag)

    def _build_lead_filters(self, base_query, filters: Dict[str, Any]):
        """Build filters for lead queries."""
        if not filters:
            return base_query
        
        conditions = []
        
        if "status" in filters:
            conditions.append(Lead.status == filters["status"])
        
        if "phone" in filters:
            conditions.append(Lead.phone.ilike(f"%{filters['phone']}%"))
        
        if "email" in filters:
            conditions.append(Lead.email.ilike(f"%{filters['email']}%"))
        
        if "name" in filters:
            name_filter = f"%{filters['name']}%"
            conditions.append(or_(
                Lead.first_name.ilike(name_filter),
                Lead.last_name.ilike(name_filter)
            ))
        
        if "tags" in filters and filters["tags"]:
            # This requires a subquery to filter by tags
            tag_subquery = (
                select(LeadTag.lead_id)
                .where(LeadTag.tag.in_(filters["tags"]))
                .group_by(LeadTag.lead_id)
                .having(func.count(LeadTag.tag) == len(filters["tags"]))
            )
            conditions.append(Lead.id.in_(tag_subquery))
        
        if "qualification" in filters:
            qual_subquery = (
                select(LeadQualification.lead_id)
                .where(and_(
                    LeadQualification.qualification == filters["qualification"],
                    LeadQualification.is_current == True
                ))
            )
            conditions.append(Lead.id.in_(qual_subquery))
        
        if "created_after" in filters:
            conditions.append(Lead.created_at >= filters["created_after"])
        
        if "created_before" in filters:
            conditions.append(Lead.created_at <= filters["created_before"])
        
        if conditions:
            return base_query.where(and_(*conditions))
        
        return base_query 