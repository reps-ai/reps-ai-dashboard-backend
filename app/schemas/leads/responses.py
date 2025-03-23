from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from app.schemas.leads.base import LeadBase
from app.schemas.common.lead_types import Tag, AssignedStaff
from app.schemas.common.activity import Call, Appointment

class LeadResponse(LeadBase):
    id: str = Field(..., description="Unique identifier for the lead")
    branch_name: str = Field(..., description="Name of the branch this lead is associated with")
    last_conversation_summary: Optional[str] = Field(
        None, 
        description="Summary of the last conversation with this lead"
    )
    last_called: Optional[str] = Field(
        None, 
        description="ISO timestamp of when the lead was last called",
        example="2025-03-20T15:30:00Z"
    )
    created_at: str = Field(
        ..., 
        description="Creation timestamp in ISO format",
        example="2025-03-15T10:00:00Z"
    )
    updated_at: str = Field(
        ..., 
        description="Last update timestamp in ISO format",
        example="2025-03-20T15:30:00Z"
    )
    score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Lead score between 0 and 1",
        example=0.85
    )
    call_count: int = Field(
        ..., 
        ge=0, 
        description="Number of calls made to or from this lead",
        example=3
    )
    appointment_date: Optional[str] = Field(
        None, 
        description="Date of the next appointment in ISO format",
        example="2025-03-25T14:00:00Z"
    )
    tags: List[Tag] = Field(
        default_factory=list, 
        description="List of tags associated with this lead"
    )
    
    @validator('last_called', 'created_at', 'updated_at', 'appointment_date')
    def validate_dates(cls, v):
        if v is not None:
            try:
                # Parse the datetime to validate format
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Date must be a valid ISO datetime format')
        return v
        
    @validator('score')
    def validate_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Score must be between 0 and 1')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "lead-123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "email": "john.doe@example.com",
                "status": "qualified",
                "branch_id": "branch-456",
                "branch_name": "Downtown Fitness",
                "source": "website",
                "interest": "Personal Training",
                "created_at": "2025-03-15T10:00:00Z",
                "updated_at": "2025-03-20T15:30:00Z",
                "score": 0.85,
                "call_count": 3,
                "last_called": "2025-03-20T15:30:00Z",
                "tags": [
                    {"id": "tag-1", "name": "VIP", "color": "#FF5733"}
                ]
            }
        }

class LeadDetailResponse(LeadResponse):
    assigned_to: Optional[AssignedStaff] = Field(
        None, 
        description="Staff member assigned to this lead"
    )
    calls: List[Call] = Field(
        default_factory=list, 
        description="List of calls associated with this lead"
    )
    appointments: List[Appointment] = Field(
        default_factory=list, 
        description="List of appointments associated with this lead"
    )

class PaginationInfo(BaseModel):
    total: int = Field(..., ge=0, description="Total number of leads available")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Number of leads per page")
    pages: int = Field(..., ge=1, description="Total number of pages available")

class LeadListResponse(BaseModel):
    data: List[LeadResponse] = Field(..., description="List of lead data")
    pagination: PaginationInfo = Field(..., description="Pagination information")