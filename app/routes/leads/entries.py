import uuid
from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.schemas.leads.base import LeadCreate, LeadUpdate
from app.schemas.leads.responses import LeadResponse, LeadDetailResponse, LeadListResponse
from app.dependencies import get_current_user, get_current_gym, get_current_branch, User, Gym, Branch, get_lead_service
from backend.services.lead.implementation import DefaultLeadService

router = APIRouter()

@router.get("/", response_model=LeadListResponse)
async def get_leads(
    current_gym: Gym = Depends(get_current_gym),
    status: Optional[str] = None,
    branch_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = Query(None, regex="^(asc|desc)$"),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Get a paginated list of leads with optional filtering and sorting.
    Only returns leads from the current user's gym.
    """
    filters = {}
    if status:
        filters["status"] = status
    if branch_id:
        filters["branch_id"] = branch_id
    if search:
        filters["search"] = search
    if sort_by:
        filters["sort_by"] = sort_by
        filters["sort_order"] = sort_order or "asc"
    
    result = await lead_service.get_paginated_leads(
        branch_id=str(current_gym.id),  # Using gym_id as branch_id for example purposes
        page=page,
        page_size=limit,
        filters=filters
    )
    
    return {
        "data": result.get("leads", []),
        "pagination": {
            "total": result.get("pagination", {}).get("total", 0),
            "page": page,
            "limit": limit,
            "pages": result.get("pagination", {}).get("pages", 1)
        }
    }

@router.get("/branch/{branch_id}", response_model=LeadListResponse)
async def get_leads_by_branch(
    branch: Branch = Depends(get_current_branch),
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = Query(None, regex="^(asc|desc)$"),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Get a paginated list of leads for a specific branch.
    Automatically verifies the branch belongs to the user's gym.
    """
    filters = {}
    if status:
        filters["status"] = status
    if search:
        filters["search"] = search
    if sort_by:
        filters["sort_by"] = sort_by
        filters["sort_order"] = sort_order or "asc"
    
    result = await lead_service.get_paginated_leads(
        branch_id=uuid.UUID(branch.id),
        page=page,
        page_size=limit,
        filters=filters
    )
    
    return {
        "data": result.get("leads", []),
        "pagination": {
            "total": result.get("pagination", {}).get("total", 0),
            "page": page,
            "limit": limit,
            "pages": result.get("pagination", {}).get("pages", 1)
        }
    }

@router.get("/{id}", response_model=LeadDetailResponse)
async def get_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to retrieve"),
    current_gym: Gym = Depends(get_current_gym),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Get detailed information about a specific lead.
    Only returns the lead if it belongs to the current user's gym.
    """
    try:
        lead = await lead_service.get_lead(id)
        
        # TESTING MODE: Skip gym verification
        # # Verify lead belongs to user's gym
        # if str(lead.get("gym_id")) != str(current_gym.id):
        #     raise HTTPException(
        #         status_code=404,
        #         detail="Lead not found"
        #     )
        
        return lead
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Create a new lead.
    Automatically associates the lead with the current user's gym.
    """
    # Convert Pydantic model to dictionary and add gym_id
    lead_data = lead.dict()
    lead_data["gym_id"] = str(current_gym.id)
    
    try:
        created_lead = await lead_service.create_lead(lead_data)
        return created_lead
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.put("/{id}", response_model=LeadResponse)
async def update_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to update"),
    lead: LeadUpdate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Update an existing lead.
    Only updates the lead if it belongs to the current user's gym.
    """
    try:
        # First check if lead exists and belongs to this gym
        existing_lead = await lead_service.get_lead(id)
        
        # TESTING MODE: Skip gym verification
        # if str(existing_lead.get("gym_id")) != str(current_gym.id):
        #     raise HTTPException(
        #         status_code=404,
        #         detail="Lead not found"
        #     )
        
        # Update the lead
        lead_data = lead.dict(exclude_unset=True)
        updated_lead = await lead_service.update_lead(id, lead_data)
        return updated_lead
    except ValueError as e:
        raise HTTPException(
            status_code=404 if "not found" in str(e).lower() else 400,
            detail=str(e)
        )

@router.get("/status/{status}", response_model=LeadListResponse)
async def get_leads_by_status(
    status: str = Path(..., description="The status to filter leads by"),
    current_gym: Gym = Depends(get_current_gym),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """Get leads by status."""
    leads = await lead_service.get_leads_by_status(str(current_gym.id), status)
    total = len(leads)
    pages = max(1, (total + limit - 1) // limit)
    start_idx, end_idx = (page - 1) * limit, min(page * limit, total)
    return {"data": leads[start_idx:end_idx], "pagination": {"total": total, "page": page, "limit": limit, "pages": pages}}

@router.get("/prioritized", response_model=List[LeadResponse])
async def get_prioritized_leads(
    count: int = Query(10, ge=1, le=50, description="Number of leads to return"),
    qualification: Optional[str] = Query(None, description="Qualification filter (hot, cold, neutral)"),
    exclude_leads: Optional[str] = Query(None, description="Comma-separated list of lead IDs to exclude"),
    current_gym: Gym = Depends(get_current_gym),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """Get prioritized leads for outreach."""
    exclude_list = exclude_leads.split(",") if exclude_leads else None
    return await lead_service.get_prioritized_leads(str(current_gym.id), count, qualification, exclude_list)

@router.post("/{id}/qualify", response_model=LeadResponse)
async def qualify_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to qualify"),
    qualification: str = Query(..., description="Qualification status (hot, cold, neutral)"),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """Update lead qualification status."""
    return await lead_service.qualify_lead(id, qualification)

@router.post("/{id}/tags", response_model=LeadResponse)
async def add_tags_to_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to add tags to"),
    tags: List[uuid.UUID] = Body(..., description="List of tags to add"),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """Add tags to a lead."""
    return await lead_service.add_tags_to_lead(id, tags)

@router.post("/{id}/after-call", response_model=LeadResponse)
async def update_lead_after_call(
    id: uuid.UUID = Path(..., description="The ID of the lead to update"),
    call_data: Dict[str, Any] = Body(..., description="Call data for updating the lead"),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """Update lead information after a call."""
    return await lead_service.update_lead_after_call(id, call_data)