from pydantic import field_validator, StringConstraints, ConfigDict, BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome
import uuid
from typing_extensions import Annotated

class CallBase(BaseModel):
    lead_id: uuid.UUID = Field(
        ..., 
        description="ID of the lead associated with this call",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    direction: str = Field(
        ..., 
        description="Direction of the call (inbound/outbound)",
        examples=["outbound"]
    )
    notes: Optional[str] = Field(
        None, 
        description="Additional notes about the call",
        examples=["Customer was interested in membership options"]
    )
    campaign_id: Optional[uuid.UUID] = Field(
        None, 
        description="ID of the campaign this call is part of",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    
    @field_validator('direction')
    @classmethod
    def validate_direction(cls, v):
        try:
            return CallDirection(v).value
        except ValueError:
            raise ValueError(f'Direction must be one of: {[d.value for d in CallDirection]}')
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "lead_id": "123e4567-e89b-12d3-a456-426614174000",
            "direction": "outbound",
            "notes": "Customer was interested in membership options",
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    })

class CallCreate(CallBase):
    scheduled_time: Optional[str] = Field(
        None, 
        description="Scheduled time for the call in ISO format (UTC)", 
        examples=["2025-03-23T10:30:00Z"]
    )
    
    @field_validator('scheduled_time')
    @classmethod
    def validate_scheduled_time(cls, v):
        if v is not None:
            try:
                # Parse the datetime to validate format
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('scheduled_time must be a valid ISO datetime format (e.g., 2025-03-23T10:30:00Z)')
        return v
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "lead_id": "123e4567-e89b-12d3-a456-426614174000",
            "direction": "outbound",
            "notes": "Follow up on previous inquiry",
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000",
            "scheduled_time": "2025-03-23T10:30:00Z"
        }
    })

class CallUpdate(BaseModel):
    outcome: Optional[str] = Field(
        None, 
        description="Outcome of the call (appointment_booked, callback_requested, not_interested, etc.)",
        examples=["appointment_booked"]
    )
    notes: Optional[str] = Field(
        None, 
        description="Additional notes about the call",
        examples=["Customer booked a consultation appointment"]
    )
    summary: Optional[str] = Field(
        None, 
        description="Summary of the call conversation",
        examples=["Discussed membership options and scheduled a visit"]
    )
    
    @field_validator('outcome')
    @classmethod
    def validate_outcome(cls, v):
        if v is not None:
            try:
                return CallOutcome(v).value
            except ValueError:
                raise ValueError(f'Outcome must be one of: {[o.value for o in CallOutcome]}')
        return v
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "outcome": "appointment_booked",
            "notes": "Customer booked a consultation appointment",
            "summary": "Discussed membership options and scheduled a visit"
        }
    })

class CallNoteCreate(BaseModel):
    content: Annotated[str, StringConstraints(min_length=1)] = Field(
        ..., 
        description="Content of the note",
        examples=["Discussed membership options"]
    )
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "content": "Discussed membership options and explained pricing tiers."
        }
    })

class CallOutcomeUpdate(BaseModel):
    outcome: str = Field(
        ..., 
        description="New outcome for the call (appointment_booked, callback_requested, not_interested, etc.)",
        examples=["appointment_booked"]
    )
    
    @field_validator('outcome')
    @classmethod
    def validate_outcome(cls, v):
        try:
            return CallOutcome(v).value
        except ValueError:
            raise ValueError(f'Outcome must be one of: {[o.value for o in CallOutcome]}')
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "outcome": "appointment_booked"
        }
    })