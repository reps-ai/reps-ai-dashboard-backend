"""
Lead processing tasks for complex operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.lead import Lead
from ...db.models.lead_tag import LeadTag
from ...db.models.lead_call import LeadCall
from ...db.models.lead_qualification import LeadQualification
from ...db.models.campaign_lead import CampaignLead
from ...db.models.call import Call
from ...utils.logging.logger import get_logger
from ...services.lead.interface import LeadService
from ...db.repositories.lead import LeadRepository
from ...db.repositories.call import CallRepository
from ...db.repositories.campaign import CampaignRepository

logger = get_logger(__name__)

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
        base_query = _build_lead_filters(base_query, filters)
    
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
        lead_data.append(await _get_lead_with_related_data(session, lead.id))
    
    return {
        "leads": lead_data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }

async def update_lead_after_call(
    session: AsyncSession,
    lead_id: str,
    call_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update lead information after a call.
    
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
        from sqlalchemy import update
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
    return await _get_lead_with_related_data(session, lead_id)

async def get_prioritized_leads(
    session: AsyncSession,
    gym_id: str,
    count: int,
    qualification: Optional[str] = None,
    exclude_leads: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Get prioritized leads for campaigns.
    
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
        return [await _get_lead_with_related_data(session, lead.id) for lead in no_calls_leads[:count]]
    
    # Get leads with oldest last call
    remaining_count = count - len(no_calls_leads)
    
    # Get the IDs of leads we already selected
    selected_ids = [lead.id for lead in no_calls_leads]
    
    # Subquery to get the latest call for each lead
    latest_call_subquery = (
        select(
            LeadCall.lead_id,
            func.max(LeadCall.call_time).label("latest_call_time")
        )
        .group_by(LeadCall.lead_id)
        .subquery()
    )
    
    # Query to get leads with oldest calls first
    oldest_calls_query = (
        select(Lead)
        .join(latest_call_subquery, Lead.id == latest_call_subquery.c.lead_id)
        .where(Lead.gym_id == gym_id)
        .where(Lead.id.not_in(selected_ids))
    )
    
    if exclude_leads:
        oldest_calls_query = oldest_calls_query.where(Lead.id.not_in(exclude_leads))
    
    if qualification:
        qual_subquery = (
            select(LeadQualification.lead_id)
            .where(and_(
                LeadQualification.qualification == qualification,
                LeadQualification.is_current == True
            ))
        )
        oldest_calls_query = oldest_calls_query.where(Lead.id.in_(qual_subquery))
    
    # Order by oldest call first, then prioritize callback status
    oldest_calls_query = (
        oldest_calls_query
        .order_by(
            # Callbacks first
            desc(Lead.status == "callback"),
            # Then by oldest call
            latest_call_subquery.c.latest_call_time
        )
        .limit(remaining_count)
    )
    
    oldest_calls_result = await session.execute(oldest_calls_query)
    oldest_calls_leads = oldest_calls_result.scalars().all()
    
    # Combine results
    all_leads = no_calls_leads + oldest_calls_leads
    
    return [await _get_lead_with_related_data(session, lead.id) for lead in all_leads]

async def get_leads_for_retry(
    session: AsyncSession,
    campaign_id: str,
    gap_days: int
) -> List[Dict[str, Any]]:
    """
    Get leads eligible for retry calls.
    
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
    
    # Subquery to get the latest call for each lead
    latest_call_subquery = (
        select(
            LeadCall.lead_id,
            func.max(LeadCall.call_time).label("latest_call_time")
        )
        .group_by(LeadCall.lead_id)
        .subquery()
    )
    
    # Query to get leads with last call before cutoff date
    retry_query = (
        select(Lead)
        .join(latest_call_subquery, Lead.id == latest_call_subquery.c.lead_id)
        .where(Lead.id.in_(campaign_lead_ids))
        .where(latest_call_subquery.c.latest_call_time < cutoff_date)
        .where(Lead.status.not_in(["closed", "converted"]))
    )
    
    retry_result = await session.execute(retry_query)
    retry_leads = retry_result.scalars().all()
    
    return [await _get_lead_with_related_data(session, lead.id) for lead in retry_leads]

# Helper functions
async def _get_lead_with_related_data(session: AsyncSession, lead_id: str) -> Optional[Dict[str, Any]]:
    """Get a lead with all related data."""
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

def _build_lead_filters(base_query, filters: Dict[str, Any]):
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

async def process_lead_after_call(
    lead_service: LeadService,
    lead_id: str,
    call_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process a lead after a call has been completed.
    
    Args:
        lead_service: Lead service instance
        lead_id: ID of the lead
        call_data: Call data including outcome, notes, etc.
        
    Returns:
        Updated lead data
    """
    logger.info(f"Processing lead {lead_id} after call {call_data.get('call_id')}")
    
    # Update lead with call information
    updated_lead = await lead_service.update_lead_after_call(lead_id, call_data)
    
    # Additional processing based on call outcome
    outcome = call_data.get("outcome")
    
    if outcome == "scheduled":
        # If lead scheduled an appointment, update status
        await lead_service.update_lead(lead_id, {"status": "scheduled"})
        logger.info(f"Lead {lead_id} scheduled an appointment")
    
    elif outcome == "not_interested":
        # If lead is not interested, update qualification
        await lead_service.qualify_lead(lead_id, "cold")
        logger.info(f"Lead {lead_id} marked as not interested")
    
    elif outcome == "callback":
        # If lead requested callback, update status and add tag
        await lead_service.update_lead(lead_id, {"status": "callback"})
        await lead_service.add_tags_to_lead(lead_id, ["callback_requested"])
        logger.info(f"Lead {lead_id} requested callback")
    
    return updated_lead

async def prioritize_leads_for_campaign(
    lead_service: LeadService,
    campaign_repository: CampaignRepository,
    gym_id: str,
    campaign_id: str,
    count: int
) -> List[Dict[str, Any]]:
    """
    Prioritize leads for a campaign.
    
    Args:
        lead_service: Lead service instance
        campaign_repository: Campaign repository instance
        gym_id: ID of the gym
        campaign_id: ID of the campaign
        count: Number of leads to prioritize
        
    Returns:
        List of prioritized leads
    """
    logger.info(f"Prioritizing leads for campaign {campaign_id}")
    
    # Get campaign details to determine qualification criteria
    campaign = await campaign_repository.get_campaign_by_id(campaign_id)
    if not campaign:
        raise ValueError(f"Campaign not found: {campaign_id}")
    
    # Get qualification from campaign settings
    qualification = campaign.get("target_qualification")
    
    # Get leads already in the campaign to exclude
    campaign_leads = await campaign_repository.get_campaign_leads(campaign_id)
    exclude_leads = [lead.get("lead_id") for lead in campaign_leads]
    
    # Get prioritized leads
    leads = await lead_service.get_prioritized_leads(
        gym_id=gym_id,
        count=count,
        qualification=qualification,
        exclude_leads=exclude_leads
    )
    
    logger.info(f"Found {len(leads)} prioritized leads for campaign {campaign_id}")
    return leads

async def process_lead_qualification(
    lead_service: LeadService,
    call_repository: CallRepository,
    lead_id: str
) -> Dict[str, Any]:
    """
    Process lead qualification based on call history and other factors.
    
    Args:
        lead_service: Lead service instance
        call_repository: Call repository instance
        lead_id: ID of the lead
        
    Returns:
        Updated lead data with new qualification
    """
    logger.info(f"Processing qualification for lead {lead_id}")
    
    # Get lead details
    lead = await lead_service.get_lead(lead_id)
    
    # Get call history
    calls = await call_repository.get_calls_by_lead(lead_id)
    
    # Determine qualification based on call history
    if not calls:
        # No calls yet, keep current qualification
        return lead
    
    # Count positive and negative outcomes
    positive_outcomes = sum(1 for call in calls if call.get("outcome") in ["interested", "scheduled"])
    negative_outcomes = sum(1 for call in calls if call.get("outcome") in ["not_interested", "no_answer"])
    
    # Determine qualification
    if positive_outcomes > negative_outcomes:
        qualification = "hot"
    elif negative_outcomes > positive_outcomes:
        qualification = "cold"
    else:
        qualification = "neutral"
    
    # Update lead qualification
    updated_lead = await lead_service.qualify_lead(lead_id, qualification)
    
    logger.info(f"Updated qualification for lead {lead_id} to {qualification}")
    return updated_lead

async def find_leads_for_retry(
    lead_service: LeadService,
    campaign_repository: CampaignRepository,
    campaign_id: str,
    gap_days: int = 7
) -> List[Dict[str, Any]]:
    """
    Find leads eligible for retry calls in a campaign.
    
    Args:
        lead_service: Lead service instance
        campaign_repository: Campaign repository instance
        campaign_id: ID of the campaign
        gap_days: Minimum days since last call
        
    Returns:
        List of leads eligible for retry
    """
    logger.info(f"Finding leads for retry in campaign {campaign_id}")
    
    # Get campaign details
    campaign = await campaign_repository.get_campaign_by_id(campaign_id)
    if not campaign:
        raise ValueError(f"Campaign not found: {campaign_id}")
    
    gym_id = campaign.get("gym_id")
    
    # Get leads in the campaign
    campaign_leads = await campaign_repository.get_campaign_leads(campaign_id)
    lead_ids = [lead.get("lead_id") for lead in campaign_leads]
    
    # Get leads with status that allows retry
    retry_statuses = ["callback", "no_answer", "busy"]
    eligible_leads = []
    
    for lead_id in lead_ids:
        lead = await lead_service.get_lead(lead_id)
        
        # Skip leads with statuses that don't allow retry
        if lead.get("status") not in retry_statuses:
            continue
        
        # Check last call date
        last_call = lead.get("last_call")
        if not last_call:
            eligible_leads.append(lead)
            continue
        
        # Check if enough time has passed since last call
        last_call_time = datetime.fromisoformat(last_call.get("call_time"))
        if datetime.now() - last_call_time >= timedelta(days=gap_days):
            eligible_leads.append(lead)
    
    logger.info(f"Found {len(eligible_leads)} leads eligible for retry in campaign {campaign_id}")
    return eligible_leads 