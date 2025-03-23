from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.common.appointment_types import AppointmentType, AppointmentStatus

class AppointmentBase(BaseModel):
    lead_id: str = Field(..., description="ID of the lead associated with this appointment")
    type: str = Field(
        ..., 
        description="Type of appointment",
        example="consultation"
    )
    date: str = Field(
        ..., 
        description="Date and time of the appointment in ISO format",
        example="2025-03-25T14:00:00Z"
    )
    duration: int = Field(
        ..., 
        ge=15, 
        le=180, 
        description="Duration of the appointment in minutes",
        example=60
    )
    status: str = Field(
        ..., 
        description="Current status of the appointment",
        example="scheduled"
    )
    branch_id: str = Field(..., description="ID of the branch where the appointment is scheduled")
    notes: Optional[str] = Field(None, description="Additional notes about the appointment")
    
    @validator('date')
    def validate_date(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('date must be a valid ISO datetime format')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        try:
            return AppointmentType(v).value
        except ValueError:
            raise ValueError(f'Type must be one of: {[t.value for t in AppointmentType]}')
    
    @validator('status')
    def validate_status(cls, v):
        try:
            return AppointmentStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[s.value for s in AppointmentStatus]}')
    
    class Config:
        use_enum_values = True

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    type: Optional[str] = Field(None, description="Type of appointment")
    date: Optional[str] = Field(None, description="Date and time of the appointment in ISO format")
    duration: Optional[int] = Field(None, ge=15, le=180, description="Duration of the appointment in minutes")
    status: Optional[str] = Field(None, description="Current status of the appointment")
    branch_id: Optional[str] = Field(None, description="ID of the branch where the appointment is scheduled")
    notes: Optional[str] = Field(None, description="Additional notes about the appointment")
    
    # Inherit validators from AppointmentBase
    _validate_date = validator('date', allow_reuse=True)(AppointmentBase.validate_date)
    _validate_type = validator('type', allow_reuse=True)(AppointmentBase.validate_type)
    _validate_status = validator('status', allow_reuse=True)(AppointmentBase.validate_status)
    
    class Config:
        use_enum_values = True

class AppointmentStatusUpdate(BaseModel):
    status: str = Field(
        ..., 
        description="New status for the appointment",
        example="completed"
    )
    
    @validator('status')
    def validate_status(cls, v):
        try:
            return AppointmentStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[s.value for s in AppointmentStatus]}')
    
    class Config:
        use_enum_values = True