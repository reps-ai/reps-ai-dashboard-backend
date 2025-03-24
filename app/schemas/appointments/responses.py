from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.schemas.appointments.base import AppointmentBase
from app.schemas.common.appointment_types import TimeSlot

class UserSummary(BaseModel):
    id: str = Field(
        ..., 
        description="Unique identifier for the user"
    )
    first_name: str = Field(
        ..., 
        description="First name of the user",
        example="John"
    )
    last_name: str = Field(
        ..., 
        description="Last name of the user",
        example="Doe"
    )

class LeadSummary(BaseModel):
    id: str = Field(
        ..., 
        description="Unique identifier for the lead"
    )
    first_name: str = Field(
        ..., 
        description="First name of the lead",
        example="John"
    )
    last_name: str = Field(
        ..., 
        description="Last name of the lead",
        example="Doe"
    )
    phone: str = Field(
        ..., 
        description="Phone number of the lead",
        example="+1234567890"
    )
    email: Optional[str] = Field(
        None, 
        description="Email address of the lead",
        example="john.doe@example.com"
    )
    status: Optional[str] = Field(
        None, 
        description="Status of the lead"
    )

class AppointmentResponse(AppointmentBase):
    id: str = Field(
        ..., 
        description="Unique identifier for the appointment"
    )
    branch_name: str = Field(
        ..., 
        description="Name of the branch where the appointment is scheduled"
    )
    created_at: str = Field(
        ..., 
        description="Creation timestamp in ISO format",
        example="2025-03-20T12:00:00Z"
    )
    lead: LeadSummary = Field(
        ..., 
        description="Summary of the lead associated with the appointment"
    )
    
    @validator('created_at')
    def validate_timestamps(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "appt-456",
                "branch_name": "Main Branch",
                "created_at": "2025-03-20T12:00:00Z",
                "lead": {
                    "id": "lead-123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1234567890",
                    "email": "john.doe@example.com"
                }
            }
        }

class AppointmentDetailResponse(AppointmentResponse):
    updated_at: str = Field(
        ..., 
        description="Last update timestamp in ISO format",
        example="2025-03-20T15:30:00Z"
    )
    created_by: UserSummary = Field(
        ..., 
        description="User who created the appointment"
    )
    reminder_sent: bool = Field(
        ..., 
        description="Whether a reminder has been sent for the appointment"
    )
    
    @validator('updated_at')
    def validate_updated_at(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format')
        return v

class AppointmentStatusResponse(BaseModel):
    id: str = Field(
        ..., 
        description="Unique identifier for the appointment status"
    )
    status: str = Field(
        ..., 
        description="Status of the appointment"
    )
    updated_at: str = Field(
        ..., 
        description="Last update timestamp in ISO format",
        example="2025-03-20T15:30:00Z"
    )
    
    @validator('updated_at')
    def validate_updated_at(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format')
        return v

class PaginationInfo(BaseModel):
    total: int = Field(..., description="Total number of appointments available", ge=0)
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Number of appointments per page")
    pages: int = Field(..., ge=1, description="Total number of pages available")

class AppointmentListResponse(BaseModel):
    data: List[AppointmentResponse] = Field(..., description="List of appointment data")
    pagination: PaginationInfo = Field(..., description="Pagination information")

class AvailabilityResponse(BaseModel):
    date: str = Field(
        ..., 
        description="Date of availability",
        example="2025-03-25"
    )
    available_slots: List[TimeSlot] = Field(
        ..., 
        description="List of available time slots"
    )