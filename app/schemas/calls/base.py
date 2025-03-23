from pydantic import BaseModel, Field, validator, constr
from typing import Optional
from datetime import datetime
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome

class CallBase(BaseModel):
    lead_id: constr(min_length=1) = Field(
        ..., 
        description="ID of the lead associated with this call",
        example="lead-123"
    )
    direction: str = Field(
        ..., 
        description="Direction of the call (inbound/outbound)",
        example="outbound"
    )
    notes: Optional[str] = Field(
        None, 
        description="Additional notes about the call",
        example="Customer was interested in membership options"
    )
    campaign_id: Optional[constr(min_length=1)] = Field(
        None, 
        description="ID of the campaign this call is part of",
        example="campaign-456"
    )
    
    @validator('direction')
    def validate_direction(cls, v):
        try:
            return CallDirection(v).value
        except ValueError:
            raise ValueError(f'Direction must be one of: {[d.value for d in CallDirection]}')
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "lead_id": "lead-123",
                "direction": "outbound",
                "notes": "Customer was interested in membership options",
                "campaign_id": "campaign-456"
            }
        }

class CallCreate(CallBase):
    scheduled_time: Optional[str] = Field(
        None, 
        description="Scheduled time for the call in ISO format (UTC)", 
        example="2025-03-23T10:30:00Z"
    )
    
    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        if v is not None:
            try:
                # Parse the datetime to validate format
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('scheduled_time must be a valid ISO datetime format (e.g., 2025-03-23T10:30:00Z)')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "lead_id": "lead-123",
                "direction": "outbound",
                "notes": "Follow up on previous inquiry",
                "campaign_id": "campaign-456",
                "scheduled_time": "2025-03-23T10:30:00Z"
            }
        }

class CallUpdate(BaseModel):
    outcome: Optional[str] = Field(
        None, 
        description="Outcome of the call (appointment_booked, callback_requested, not_interested, etc.)",
        example="appointment_booked"
    )
    notes: Optional[str] = Field(
        None, 
        description="Additional notes about the call",
        example="Customer booked a consultation appointment"
    )
    summary: Optional[str] = Field(
        None, 
        description="Summary of the call conversation",
        example="Discussed membership options and scheduled a visit"
    )
    
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
        schema_extra = {
            "example": {
                "outcome": "appointment_booked",
                "notes": "Customer booked a consultation appointment",
                "summary": "Discussed membership options and scheduled a visit"
            }
        }

class CallNoteCreate(BaseModel):
    content: constr(min_length=1) = Field(
        ..., 
        description="Content of the note",
        example="Discussed membership options"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Discussed membership options and explained pricing tiers."
            }
        }

class CallOutcomeUpdate(BaseModel):
    outcome: str = Field(
        ..., 
        description="New outcome for the call (appointment_booked, callback_requested, not_interested, etc.)",
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
        schema_extra = {
            "example": {
                "outcome": "appointment_booked"
            }
        }