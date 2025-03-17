from fastapi import APIRouter, Query, Path, Body
from typing import Optional, List

from app.schemas.leads.base import LeadCreate, LeadUpdate
from app.schemas.leads.responses import LeadResponse, LeadDetailResponse, LeadListResponse

router = APIRouter()

@router.get("", response_model=LeadListResponse)
async def get_leads(
    status: Optional[str] = None,
    branch_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = Query(None, regex="^(asc|desc)$")
):
    """
    Get a paginated list of leads with optional filtering and sorting.
    """
    # Implementation will be added later
    pass

@router.get("/{id}", response_model=LeadDetailResponse)
async def get_lead(
    id: str = Path(..., description="The ID of the lead to retrieve")
):
    """
    Get detailed information about a specific lead.
    """
    # Implementation will be added later
    pass

@router.post("", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate = Body(...)
):
    """
    Create a new lead.
    """
    # Implementation will be added later
    pass

@router.put("/{id}", response_model=LeadResponse)
async def update_lead(
    id: str = Path(..., description="The ID of the lead to update"),
    lead: LeadUpdate = Body(...)
):
    """
    Update an existing lead.
    """
    # Implementation will be added later
    pass 