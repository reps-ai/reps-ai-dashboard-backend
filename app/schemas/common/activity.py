from pydantic import field_validator, ConfigDict, BaseModel, Field
from typing import Optional
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome, CallSentiment
from app.schemas.common.appointment_types import AppointmentStatus, AppointmentType

class Call(BaseModel):
    id: str = Field(..., description="Unique identifier for the call")
    direction: str = Field(
        ..., 
        description="Direction of the call (inbound/outbound)",
        examples=["outbound"]
    )
    status: str = Field(
        ..., 
        description="Current status of the call",
        examples=["completed"]
    )
    start_time: str = Field(
        ..., 
        description="Start time of the call in ISO format",
        examples=["2025-03-23T10:00:00Z"]
    )
    duration: int = Field(
        ..., 
        ge=0, 
        description="Duration of the call in seconds",
        examples=[300]
    )
    outcome: str = Field(
        ..., 
        description="Outcome of the call",
        examples=["appointment_booked"]
    )
    sentiment: str = Field(
        ..., 
        description="Detected sentiment of the call",
        examples=["positive"]
    )
    summary: str = Field(
        ..., 
        description="Summary of the call conversation",
        examples=["Customer inquired about membership options and booked a consultation appointment."]
    )
    
    @field_validator('direction')
    @classmethod
    def validate_direction(cls, v):
        try:
            return CallDirection(v).value
        except ValueError:
            raise ValueError(f'Direction must be one of: {[d.value for d in CallDirection]}')
            
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        try:
            return CallStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[s.value for s in CallStatus]}')
            
    @field_validator('outcome')
    @classmethod
    def validate_outcome(cls, v):
        try:
            return CallOutcome(v).value
        except ValueError:
            raise ValueError(f'Outcome must be one of: {[o.value for o in CallOutcome]}')
    
    @field_validator('sentiment')
    @classmethod
    def validate_sentiment(cls, v):
        try:
            return CallSentiment(v).value
        except ValueError:
            raise ValueError(f'Sentiment must be one of: {[s.value for s in CallSentiment]}')
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "id": "call-123",
            "direction": "outbound",
            "status": "completed",
            "start_time": "2025-03-23T10:00:00Z",
            "duration": 300,
            "outcome": "appointment_booked",
            "sentiment": "positive",
            "summary": "Customer showed interest in premium membership and scheduled a visit."
        }
    })

class Appointment(BaseModel):
    id: str = Field(..., description="Unique identifier for the appointment")
    type: str = Field(
        ..., 
        description="Type of the appointment",
        examples=["consultation"]
    )
    date: str = Field(
        ..., 
        description="Date and time of the appointment in ISO format",
        examples=["2025-03-25T14:00:00Z"]
    )
    duration: int = Field(
        ..., 
        ge=15, 
        description="Duration of the appointment in minutes",
        examples=[60]
    )
    status: str = Field(
        ..., 
        description="Current status of the appointment",
        examples=["scheduled"]
    )
    branch_name: str = Field(
        ..., 
        description="Name of the branch where the appointment is scheduled",
        examples=["Downtown Fitness Center"]
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        try:
            return AppointmentType(v).value
        except ValueError:
            raise ValueError(f'Type must be one of: {[t.value for t in AppointmentType]}')
            
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        try:
            return AppointmentStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[s.value for s in AppointmentStatus]}')
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "id": "appt-456",
            "type": "consultation",
            "date": "2025-03-25T14:00:00Z",
            "duration": 60,
            "status": "scheduled",
            "branch_name": "Downtown Fitness Center"
        }
    })