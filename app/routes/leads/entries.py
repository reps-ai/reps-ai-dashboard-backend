from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.leads.base import LeadCreate, LeadUpdate
from app.schemas.leads.responses import LeadResponse, LeadDetailResponse, LeadListResponse
from app.dependencies import get_current_user, get_current_gym, get_current_branch, User, Gym, Branch

# Import the database dependency and lead service
from backend.db.connections.database import get_db
from backend.services.lead.factory import LeadServiceFactory

router = APIRouter()

@router.get("", response_model=LeadListResponse)
async def get_leads(
    current_gym: Gym = Depends(get_current_gym),
    status: Optional[str] = None,
    branch_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = Query(None, regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of leads with optional filtering and sorting.
    Only returns leads from the current user's gym.
    """
    # Create the lead service
    lead_service = await LeadServiceFactory.create_service(db)
    
    # Get leads from the database
    leads_result = await lead_service.get_leads(
        gym_id=current_gym.id,
        status=status,
        branch_id=branch_id,
        search_term=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Return response
    return {
        "items": leads_result.get("items", []),
        "total": leads_result.get("total", 0),
        "page": page,
        "limit": limit,
        "pages": (leads_result.get("total", 0) + limit - 1) // limit
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
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of leads for a specific branch.
    Automatically verifies the branch belongs to the user's gym.
    """
    # Create the lead service
    lead_service = await LeadServiceFactory.create_service(db)
    
    # Get leads from the database
    leads_result = await lead_service.get_leads(
        gym_id=branch.gym_id,
        branch_id=branch.id,
        status=status,
        search_term=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Return response
    return {
        "items": leads_result.get("items", []),
        "total": leads_result.get("total", 0),
        "page": page,
        "limit": limit,
        "pages": (leads_result.get("total", 0) + limit - 1) // limit
    }

@router.get("/{id}", response_model=LeadDetailResponse)
async def get_lead(
    id: str = Path(..., description="The ID of the lead to retrieve"),
    current_gym: Gym = Depends(get_current_gym),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific lead.
    Only returns the lead if it belongs to the current user's gym.
    """
    # Create the lead service
    lead_service = await LeadServiceFactory.create_service(db)
    
    # Get the lead from the database
    lead = await lead_service.get_lead_by_id(id)
    
    # Check if lead exists and belongs to the current gym
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    if lead.get("gym_id") != current_gym.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    return lead

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead: LeadCreate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new lead.
    Automatically associates the lead with the current user's gym.
    """
    # Create the lead service
    lead_service = await LeadServiceFactory.create_service(db)
    
    # Prepare lead data with gym_id
    lead_data = lead.dict()
    lead_data["gym_id"] = current_gym.id
    lead_data["created_by_user_id"] = current_user.id
    
    # Create the lead in the database
    created_lead = await lead_service.create_lead(lead_data)
    
    return created_lead

@router.put("/{id}", response_model=LeadResponse)
async def update_lead(
    id: str = Path(..., description="The ID of the lead to update"),
    lead: LeadUpdate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing lead.
    Only updates the lead if it belongs to the current user's gym.
    """
    # Create the lead service
    lead_service = await LeadServiceFactory.create_service(db)
    
    # Get the existing lead
    existing_lead = await lead_service.get_lead_by_id(id)
    
    # Check if lead exists and belongs to the current gym
    if not existing_lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    if existing_lead.get("gym_id") != current_gym.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    # Update the lead in the database
    updated_lead = await lead_service.update_lead(id, lead.dict(exclude_unset=True))
    
    return updated_lead

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    id: str = Path(..., description="The ID of the lead to delete"),
    current_gym: Gym = Depends(get_current_gym),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a lead.
    Only deletes the lead if it belongs to the current user's gym.
    """
    # Create the lead service
    lead_service = await LeadServiceFactory.create_service(db)
    
    # Get the existing lead
    existing_lead = await lead_service.get_lead_by_id(id)
    
    # Check if lead exists and belongs to the current gym
    if not existing_lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    if existing_lead.get("gym_id") != current_gym.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    # Delete the lead
    await lead_service.delete_lead(id)
    
    return None 