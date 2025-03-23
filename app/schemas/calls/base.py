from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome

class CallBase(BaseModel):
    lead_id: str = Field(..., description="ID of the lead associated with this call")
    direction: str = Field(
        ..., 
        description="Direction of the call (inbound/outbound)",
        example="outbound"
    )
    notes: Optional[str] = Field(None, description="Additional notes about the call")
    campaign_id: Optional[str] = Field(None, description="ID of the campaign this call is part of")
    
    @validator('direction')
    def validate_direction(cls, v):
        try:
            return CallDirection(v).value
        except ValueError:
            raise ValueError(f'Direction must be one of: {[d.value for d in CallDirection]}')
    
    class Config:
        use_enum_values = True

class CallCreate(CallBase):
    scheduled_time: Optional[str] = Field(
        None, 
        description="Scheduled time for the call in ISO format", 
        example="2025-03-23T10:30:00Z"
    )
    
    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        if v is not None:
            try:
                # Parse the datetime to validate format
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('scheduled_time must be a valid ISO datetime format')
        return v

class CallUpdate(BaseModel):
    outcome: Optional[str] = Field(
        None, 
        description="Outcome of the call",
        example="appointment_booked"
    )
    notes: Optional[str] = Field(None, description="Additional notes about the call")
    summary: Optional[str] = Field(None, description="Summary of the call conversation")
    
    @validator('outcome')
    def validate_outcome(cls, v):
        if v is not None:
            try:
                return CallOutcome(v).value
            except ValueError:
                raise ValueError(f'Outcome must be one of: {[o.value for o in CallOutcome]}')
        return v
    
    class Config:
        use_enum_values = True

class CallNoteCreate(BaseModel):
    content: str = Field(
        ..., 
        min_length=1, 
        description="Content of the note",
        example="Discussed membership options"
    )

class CallOutcomeUpdate(BaseModel):
    outcome: str = Field(
        ..., 
        description="New outcome for the call",
        example="appointment_booked"
    )
    
    @validator('outcome')
    def validate_outcome(cls, v):
        try:
            return CallOutcome(v).value
        except ValueError:
            raise ValueError(f'Outcome must be one of: {[o.value for o in CallOutcome]}')
    
    class Config:
        use_enum_values = True