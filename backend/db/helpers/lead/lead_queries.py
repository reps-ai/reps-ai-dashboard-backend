"""
Database helper functions for lead-related operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.lead import Lead
from ...models.lead_tag import LeadTag
from ...models.lead_call import LeadCall
from ...models.lead_qualification import LeadQualification
from ...models.campaign_lead import CampaignLead
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

async def get_lead_with_related_data(session: AsyncSession, lead_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a lead with all related data.
    
    Args:
        session: Database session
        lead_id: Lead ID
        
    Returns:
        Lead data with related information or None if not found
    """
    # Get lead
    lead_query = select(Lead).where(Lead.id == lead_id)
    lead_result = await session.execute(lead_query)
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        return None
    
    lead_dict = lead.to_dict()
    
    # Get tags
    tags_query = select(LeadTag.tag).where(LeadTag.lead_id == lead_id)
    tags_result = await session.execute(tags_query)
    lead_dict["tags"] = [row[0] for row in tags_result]
    
    # Get current qualification
    qual_query = (
        select(LeadQualification)
        .where(and_(
            LeadQualification.lead_id == lead_id,
            LeadQualification.is_current == True
        ))
    )
    qual_result = await session.execute(qual_query)
    qualification = qual_result.scalar_one_or_none()
    lead_dict["qualification"] = qualification.qualification if qualification else None
    
    # Get last call
    call_query = (
        select(LeadCall)
        .where(LeadCall.lead_id == lead_id)
        .order_by(desc(LeadCall.call_time))
        .limit(1)
    )
    call_result = await session.execute(call_query)
    last_call = call_result.scalar_one_or_none()
    lead_dict["last_call"] = last_call.to_dict() if last_call else None
    
    return lead_dict

def build_lead_filters(base_query, filters: Dict[str, Any]):
    """
    Build query filters for lead queries.
    
    Args:
        base_query: Base SQLAlchemy query
        filters: Dictionary of filters
        
    Returns:
        Query with filters applied
    """
    conditions = []
    
    # Status filter
    if "status" in filters:
        status = filters["status"]
        if isinstance(status, list):
            conditions.append(Lead.status.in_(status))
        else:
            conditions.append(Lead.status == status)
    
    # Search filter (name, email, phone)
    if "search" in filters and filters["search"]:
        search_term = f"%{filters['search']}%"
        conditions.append(or_(
            Lead.name.ilike(search_term),
            Lead.email.ilike(search_term),
            Lead.phone.ilike(search_term)
        ))
    
    # Date range filter
    if "date_from" in filters:
        conditions.append(Lead.created_at >= filters["date_from"])
    
    if "date_to" in filters:
        conditions.append(Lead.created_at <= filters["date_to"])
    
    # Tag filter
    if "tags" in filters and filters["tags"]:
        tags = filters["tags"]
        if isinstance(tags, list):
            tag_subquery = (
                select(LeadTag.lead_id)
                .where(LeadTag.tag.in_(tags))
                .group_by(LeadTag.lead_id)
                .having(func.count(LeadTag.tag) == len(tags))
            )
        else:
            tag_subquery = select(LeadTag.lead_id).where(LeadTag.tag == tags)
        
        conditions.append(Lead.id.in_(tag_subquery))
    
    # Qualification filter
    if "qualification" in filters:
        qualification = filters["qualification"]
        qual_subquery = (
            select(LeadQualification.lead_id)
            .where(and_(
                LeadQualification.qualification == qualification,
                LeadQualification.is_current == True
            ))
        )
        conditions.append(Lead.id.in_(qual_subquery))
    
    # Campaign filter
    if "campaign_id" in filters:
        campaign_subquery = select(CampaignLead.lead_id).where(
            CampaignLead.campaign_id == filters["campaign_id"]
        )
        conditions.append(Lead.id.in_(campaign_subquery))
    
    if conditions:
        return base_query.where(and_(*conditions))
    
    return base_query

async def get_leads_by_gym_with_filters(
    session: AsyncSession,
    gym_id: str,
    filters: Optional[Dict[str, Any]] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all leads for a gym with optional filters.
    
    Args:
        session: Database session
        gym_id: Gym ID
        filters: Optional filters
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing leads and pagination info
    """
    # Start with base query
    base_query = select(Lead).where(Lead.gym_id == gym_id)
    
    # Apply filters
    if filters:
        base_query = build_lead_filters(base_query, filters)
    
    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.execute(count_query)
    total = total_count.scalar_one()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = base_query.order_by(desc(Lead.created_at)).offset(offset).limit(page_size)
    
    # Execute query
    result = await session.execute(query)
    leads = result.scalars().all()
    
    # Get full lead data
    lead_data = []
    for lead in leads:
        lead_data.append(await get_lead_with_related_data(session, lead.id))
    
    return {
        "leads": lead_data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }

async def update_lead_after_call_db(
    session: AsyncSession,
    lead_id: str,
    call_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update lead information after a call in the database.
    
    Args:
        session: Database session
        lead_id: Lead ID
        call_data: Call data
        
    Returns:
        Updated lead data if successful, None if lead not found
    """
    # Check if lead exists
    lead_query = select(Lead).where(Lead.id == lead_id)
    lead_result = await session.execute(lead_query)
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        return None
    
    # Create call record
    call_record = LeadCall(
        lead_id=lead_id,
        call_id=call_data.get("call_id"),
        call_time=datetime.now(),
        duration=call_data.get("duration", 0),
        outcome=call_data.get("outcome"),
        notes=call_data.get("notes")
    )
    session.add(call_record)
    
    # Update lead based on call outcome
    updates = {}
    
    # Update status based on outcome
    outcome = call_data.get("outcome")
    if outcome == "scheduled":
        updates["status"] = "scheduled"
    elif outcome == "not_interested":
        updates["status"] = "closed"
    elif outcome == "callback":
        updates["status"] = "callback"
    
    # Update qualification if provided
    qualification = call_data.get("qualification")
    if qualification:
        # Set all current qualifications to not current
        update_query = (
            update(LeadQualification)
            .where(and_(
                LeadQualification.lead_id == lead_id,
                LeadQualification.is_current == True
            ))
            .values(is_current=False)
        )
        await session.execute(update_query)
        
        # Create new qualification record
        new_qualification = LeadQualification(
            lead_id=lead_id,
            qualification=qualification,
            is_current=True,
            created_at=datetime.now()
        )
        session.add(new_qualification)
    
    # Update lead record if needed
    if updates:
        update_query = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(**updates)
        )
        await session.execute(update_query)
    
    # Add tags if provided
    tags = call_data.get("tags", [])
    if tags:
        # Get existing tags
        existing_tags_query = select(LeadTag.tag).where(LeadTag.lead_id == lead_id)
        existing_tags_result = await session.execute(existing_tags_query)
        existing_tags = [row[0] for row in existing_tags_result]
        
        # Add only new tags
        new_tags = [tag for tag in tags if tag not in existing_tags]
        for tag in new_tags:
            lead_tag = LeadTag(lead_id=lead_id, tag=tag)
            session.add(lead_tag)
    
    await session.commit()
    
    # Get updated lead data
    return await get_lead_with_related_data(session, lead_id)

async def get_prioritized_leads_db(
    session: AsyncSession,
    gym_id: str,
    count: int,
    qualification: Optional[str] = None,
    exclude_leads: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Get prioritized leads for campaigns from the database.
    
    Args:
        session: Database session
        gym_id: Gym ID
        count: Number of leads to return
        qualification: Optional qualification filter
        exclude_leads: Optional list of lead IDs to exclude
        
    Returns:
        List of prioritized lead data
    """
    # Start with base query
    base_query = select(Lead).where(Lead.gym_id == gym_id)
    
    # Apply qualification filter if provided
    if qualification:
        qual_subquery = (
            select(LeadQualification.lead_id)
            .where(and_(
                LeadQualification.qualification == qualification,
                LeadQualification.is_current == True
            ))
        )
        base_query = base_query.where(Lead.id.in_(qual_subquery))
    
    # Exclude leads if provided
    if exclude_leads:
        base_query = base_query.where(Lead.id.not_in(exclude_leads))
    
    # Prioritize leads:
    # 1. Leads with no calls
    # 2. Leads with oldest last call
    # 3. Leads with callback status
    
    # Get leads with no calls
    no_calls_subquery = (
        select(Lead.id)
        .outerjoin(LeadCall, Lead.id == LeadCall.lead_id)
        .where(LeadCall.id == None)
        .where(Lead.gym_id == gym_id)
    )
    
    if qualification:
        qual_subquery = (
            select(LeadQualification.lead_id)
            .where(and_(
                LeadQualification.qualification == qualification,
                LeadQualification.is_current == True
            ))
        )
        no_calls_subquery = no_calls_subquery.where(Lead.id.in_(qual_subquery))
    
    if exclude_leads:
        no_calls_subquery = no_calls_subquery.where(Lead.id.not_in(exclude_leads))
    
    no_calls_query = select(Lead).where(Lead.id.in_(no_calls_subquery)).limit(count)
    no_calls_result = await session.execute(no_calls_query)
    no_calls_leads = no_calls_result.scalars().all()
    
    # If we have enough leads with no calls, return them
    if len(no_calls_leads) >= count:
        return [await get_lead_with_related_data(session, lead.id) for lead in no_calls_leads[:count]]
    
    # Get leads with oldest last call
    remaining_count = count - len(no_calls_leads)
    
    # Subquery to get the last call time for each lead
    last_call_subquery = (
        select(
            LeadCall.lead_id,
            func.max(LeadCall.call_time).label("last_call_time")
        )
        .group_by(LeadCall.lead_id)
        .subquery()
    )
    
    oldest_calls_query = (
        select(Lead)
        .join(last_call_subquery, Lead.id == last_call_subquery.c.lead_id)
        .where(Lead.gym_id == gym_id)
    )
    
    if qualification:
        qual_subquery = (
            select(LeadQualification.lead_id)
            .where(and_(
                LeadQualification.qualification == qualification,
                LeadQualification.is_current == True
            ))
        )
        oldest_calls_query = oldest_calls_query.where(Lead.id.in_(qual_subquery))
    
    if exclude_leads:
        oldest_calls_query = oldest_calls_query.where(Lead.id.not_in(exclude_leads))
    
    # Exclude leads we already have
    no_calls_ids = [lead.id for lead in no_calls_leads]
    if no_calls_ids:
        oldest_calls_query = oldest_calls_query.where(Lead.id.not_in(no_calls_ids))
    
    oldest_calls_query = oldest_calls_query.order_by(last_call_subquery.c.last_call_time).limit(remaining_count)
    oldest_calls_result = await session.execute(oldest_calls_query)
    oldest_calls_leads = oldest_calls_result.scalars().all()
    
    # Combine results
    all_leads = list(no_calls_leads) + list(oldest_calls_leads)
    
    return [await get_lead_with_related_data(session, lead.id) for lead in all_leads]

async def get_leads_for_retry_db(
    session: AsyncSession,
    campaign_id: str,
    gap_days: int
) -> List[Dict[str, Any]]:
    """
    Get leads eligible for retry calls from the database.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        gap_days: Minimum days since last call
        
    Returns:
        List of lead data eligible for retry
    """
    # Get campaign leads
    campaign_leads_query = select(CampaignLead.lead_id).where(CampaignLead.campaign_id == campaign_id)
    campaign_leads_result = await session.execute(campaign_leads_query)
    campaign_lead_ids = [row[0] for row in campaign_leads_result]
    
    if not campaign_lead_ids:
        return []
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=gap_days)
    
    # Subquery to get the last call time for each lead
    last_call_subquery = (
        select(
            LeadCall.lead_id,
            func.max(LeadCall.call_time).label("last_call_time")
        )
        .where(LeadCall.lead_id.in_(campaign_lead_ids))
        .group_by(LeadCall.lead_id)
        .subquery()
    )
    
    # Get leads with last call before cutoff date
    retry_query = (
        select(Lead)
        .join(last_call_subquery, Lead.id == last_call_subquery.c.lead_id)
        .where(last_call_subquery.c.last_call_time < cutoff_date)
    )
    
    retry_result = await session.execute(retry_query)
    retry_leads = retry_result.scalars().all()
    
    return [await get_lead_with_related_data(session, lead.id) for lead in retry_leads] 