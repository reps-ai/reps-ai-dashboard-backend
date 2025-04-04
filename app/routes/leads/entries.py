import uuid
from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.leads.base import LeadCreate, LeadCreateInput, LeadUpdate, LeadStatusUpdate
from app.schemas.leads.responses import LeadResponse, LeadDetailResponse, LeadListResponse
from app.dependencies import get_current_user, get_current_gym, get_current_branch, User, Gym, Branch, get_lead_service
from backend.services.lead.implementation import DefaultLeadService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def format_lead_for_response(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format lead data to match the expected LeadResponse schema.
    Ensures consistent data types and field names.
    """
    # Handle fields that may have different names or formats
    # Normalize score to be between 0 and 1
    score = 0.0
    if lead.get("score") is not None:
        try:
            score_val = float(lead.get("score", 0))
            # Ensure score is between 0 and 1
            score = min(max(score_val, 0.0), 1.0)
        except (TypeError, ValueError):
            score = 0.0
    
    # Ensure source is one of the allowed values
    valid_sources = ['website', 'referral', 'walk_in', 'phone', 'social', 'other']
    source = lead.get("source", "other")
    if source not in valid_sources:
        source = "other"
    
    # Ensure status is one of the allowed values
    valid_statuses = ['new', 'contacted', 'qualified', 'converted', 'lost']
    status = lead.get("lead_status", lead.get("status", "new"))
    if status not in valid_statuses:
        status = "new"
    
    formatted_lead = {
        "id": str(lead.get("id", "")),
        "first_name": lead.get("first_name", ""),
        "last_name": lead.get("last_name", ""),
        "phone": lead.get("phone", ""),
        "email": lead.get("email"),
        "status": status,
        "source": source,
        "branch_id": str(lead.get("branch_id", "")),
        "branch_name": lead.get("branch_name", ""),
        "notes": lead.get("notes", ""),
        "interest": lead.get("interest", ""),
        "interest_location": lead.get("interest_location", ""),
        "last_conversation_summary": lead.get("last_conversation_summary"),
        "score": score,
        "call_count": int(lead.get("call_count", 0)),
    }
    
    # Handle dates - ensure they're all in ISO format
    for date_field in ["created_at", "updated_at"]:
        if lead.get(date_field):
            if isinstance(lead[date_field], str):
                formatted_lead[date_field] = lead[date_field]
            else:
                formatted_lead[date_field] = lead[date_field].isoformat()
        else:
            formatted_lead[date_field] = datetime.now().isoformat()
    
    # Handle last_called (may be None)
    if lead.get("last_called"):
        if isinstance(lead["last_called"], str):
            formatted_lead["last_called"] = lead["last_called"]
        else:
            formatted_lead["last_called"] = lead["last_called"].isoformat()
    else:
        formatted_lead["last_called"] = None
        
    # Handle appointment_date (may be None or stored as next_appointment_date)
    appointment_date = lead.get("appointment_date", lead.get("next_appointment_date"))
    if appointment_date:
        if isinstance(appointment_date, str):
            formatted_lead["appointment_date"] = appointment_date
        else:
            formatted_lead["appointment_date"] = appointment_date.isoformat()
    else:
        formatted_lead["appointment_date"] = None
    
    # Format tags
    tags = []
    if lead.get("tags"):
        for tag in lead["tags"]:
            tags.append({
                "id": str(tag.get("id", "")),
                "name": tag.get("name", ""),
                # Add a default color if none is present
                "color": tag.get("color") or "#888888"
            })
    formatted_lead["tags"] = tags
    
    return formatted_lead

def normalize_lead_status(lead_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ensure all leads have valid status values according to the schema.
    """
    valid_statuses = ['new', 'contacted', 'qualified', 'converted', 'lost']
    
    for lead in lead_list:
        if lead.get("status") not in valid_statuses:
            # Default to "new" if status is invalid
            lead["status"] = "new"
    
    return lead_list

@router.get("/", response_model=LeadListResponse)
async def get_leads(
    current_gym: Gym = Depends(get_current_gym),
    current_branch: Branch = Depends(get_current_branch),
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
    
    try:
        result = await lead_service.get_paginated_leads(
            branch_id=str(current_branch.id),
            page=page,
            page_size=limit,
            filters=filters
        )
        
        # Format each lead to match the expected schema
        formatted_leads = [format_lead_for_response(lead) for lead in result.get("leads", [])]
        
        # Normalize lead statuses to ensure they match allowed values
        formatted_leads = normalize_lead_status(formatted_leads)
        
        # Ensure pages is at least 1 to satisfy validation
        pages = result.get("pagination", {}).get("pages", 1)
        if pages < 1:
            pages = 1
        
        return {
            "data": formatted_leads,
            "pagination": {
                "total": result.get("pagination", {}).get("total", 0),
                "page": page,
                "limit": limit,
                "pages": pages
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

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
    
    try:
        result = await lead_service.get_paginated_leads(
            branch_id=str(branch.id),
            page=page,
            page_size=limit,
            filters=filters
        )
        
        # Format each lead to match the expected schema
        formatted_leads = [format_lead_for_response(lead) for lead in result.get("leads", [])]
        
        # Normalize lead statuses to ensure they match allowed values
        formatted_leads = normalize_lead_status(formatted_leads)
        
        # Ensure pages is at least 1 to satisfy validation
        pages = result.get("pagination", {}).get("pages", 1)
        if pages < 1:
            pages = 1
        
        return {
            "data": formatted_leads,
            "pagination": {
                "total": result.get("pagination", {}).get("total", 0),
                "page": page,
                "limit": limit,
                "pages": pages
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/prioritized", response_model=List[LeadResponse])
async def get_prioritized_leads(
    count: int = Query(10, ge=1, le=50, description="Number of leads to return"),
    qualification: Optional[str] = Query(None, description="Qualification filter (hot, cold, neutral)"),
    exclude_leads: Optional[str] = Query(None, description="Comma-separated list of lead IDs to exclude"),
    current_gym: Gym = Depends(get_current_gym),
    current_branch: Branch = Depends(get_current_branch),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """Get prioritized leads for outreach."""
    try:
        exclude_list = exclude_leads.split(",") if exclude_leads else None
        logger.info(f"Retrieving prioritized leads for branch: {current_branch.id}")
        leads = await lead_service.get_prioritized_leads(str(current_branch.id), count, qualification, exclude_list)
        
        # Format leads to match the expected schema
        formatted_leads = [format_lead_for_response(lead) for lead in leads]
        
        # Normalize lead statuses to ensure they match allowed values
        formatted_leads = normalize_lead_status(formatted_leads)
        
        return formatted_leads
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving prioritized leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

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
        logger.info(f"Fetching lead with ID: {id}")
        lead = await lead_service.get_lead(str(id))
        
        # Verify lead belongs to user's gym
        if str(lead.get("gym_id")) != str(current_gym.id):
            logger.warning(f"Lead {id} does not belong to gym {current_gym.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found or does not belong to your gym"
            )
        
        # Format lead to match the expected schema
        try:
            logger.debug(f"Formatting lead data for ID: {id}")
            formatted_lead = format_lead_for_response(lead)
            return formatted_lead
        except Exception as format_error:
            logger.error(f"Error formatting lead data: {str(format_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error formatting lead data: {str(format_error)}"
            )
    except ValueError as e:
        logger.error(f"Value error retrieving lead {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead not found: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Error retrieving lead {id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the lead"
        )

@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreateInput = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    current_branch: Branch = Depends(get_current_branch),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Create a new lead.
    Automatically associates the lead with the current user's gym and branch.
    """
    # Convert Pydantic model to dictionary
    lead_data = lead.dict()
    
    # Add gym_id and branch_id from the dependencies
    lead_data["gym_id"] = str(current_gym.id)
    lead_data["branch_id"] = str(current_branch.id)
    
    # Log the assigned branch for debugging
    logger.info(f"Creating new lead assigned to branch: {current_branch.id} (Gym: {current_gym.id})")
    
    # Map "status" field to "lead_status" field expected by the database model
    if "status" in lead_data:
        lead_data["lead_status"] = lead_data.pop("status")
    
    # Extract tags for later processing
    tags = None
    if "tags" in lead_data and lead_data["tags"]:
        tags = [str(tag) for tag in lead_data["tags"]]
        # Remove tags from lead_data as they're processed separately
        lead_data.pop("tags")
    
    try:
        # Create the lead without tags first
        created_lead = await lead_service.create_lead(lead_data)
        
        # If we have tags, add them to the lead in a separate operation
        if tags and len(tags) > 0:
            lead_id = created_lead["id"]
            created_lead = await lead_service.add_tags_to_lead(str(lead_id), tags)
        
        # Format created lead to match the expected schema
        formatted_lead = format_lead_for_response(created_lead)
        return formatted_lead
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.put("/{id}", response_model=LeadResponse)
async def update_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to update"),
    lead: LeadUpdate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    current_branch: Branch = Depends(get_current_branch),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Update an existing lead.
    Only updates the lead if it belongs to the current user's gym.
    """
    try:
        # First check if lead exists and belongs to this gym
        existing_lead = await lead_service.get_lead(str(id))
        
        if str(existing_lead.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found or does not belong to your gym"
            )
        
        # Update the lead, but ensure branch_id can't be changed by user
        lead_data = lead.dict(exclude_unset=True)
        
        # Remove branch_id if it exists in the input data
        if "branch_id" in lead_data:
            logger.warning(f"Attempt to modify branch_id for lead {id} - ignoring this field")
            lead_data.pop("branch_id")
        
        updated_lead = await lead_service.update_lead(str(id), lead_data)
        
        # Format updated lead to match the expected schema
        formatted_lead = format_lead_for_response(updated_lead)
        return formatted_lead
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/{id}/tags", response_model=LeadResponse)
async def add_tags_to_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to add tags to"),
    tags: List[uuid.UUID] = Body(..., description="List of tags to add"),
    current_branch: Branch = Depends(get_current_branch),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """Add tags to a lead."""
    try:
        # Verify lead belongs to user's gym
        existing_lead = await lead_service.get_lead(str(id))
        if str(existing_lead.get("branch_id")) != str(current_branch.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found or does not belong to your gym"
            )
            
        lead = await lead_service.add_tags_to_lead(str(id), [str(tag) for tag in tags])
        
        # Format lead to match the expected schema
        formatted_lead = format_lead_for_response(lead)
        return formatted_lead
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.delete("/{id}/tags", response_model=LeadResponse)
async def remove_tags_from_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to remove tags from"),
    tags: List[uuid.UUID] = Body(..., description="List of tag IDs to remove"),
    current_branch: Branch = Depends(get_current_branch),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Remove tags from a lead.
    Only removes tags if the lead belongs to the current user's gym.
    """
    try:
        # Verify lead belongs to user's gym
        existing_lead = await lead_service.get_lead(str(id))
        if str(existing_lead.get("branch_id")) != str(current_branch.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found or does not belong to your gym"
            )
            
        # Convert UUIDs to strings
        tag_ids = [str(tag) for tag in tags]
        
        # Call service method to remove tags
        lead = await lead_service.remove_tags_from_lead(str(id), tag_ids)
        
        # Format lead to match the expected schema
        formatted_lead = format_lead_for_response(lead)
        return formatted_lead
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing tags from lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete("/{id}", response_model=Dict[str, str])
async def delete_lead(
    id: uuid.UUID = Path(..., description="The ID of the lead to delete"),
    current_gym: Gym = Depends(get_current_gym),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Delete a lead.
    Only deletes the lead if it belongs to the current user's gym.
    """
    try:
        # First check if lead exists and belongs to this gym
        existing_lead = await lead_service.get_lead(str(id))
        
        if str(existing_lead.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found or does not belong to your gym"
            )
        
        # Delete the lead
        await lead_service.delete_lead(str(id))
        
        return {"message": "Lead successfully deleted"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
