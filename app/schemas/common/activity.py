from pydantic import BaseModel, Field, validator
from typing import Optional
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome, CallSentiment
from app.schemas.common.appointment_types import AppointmentStatus, AppointmentType

class Call(BaseModel):
    id: str = Field(..., description="Unique identifier for the call")
    direction: str = Field(
        ..., 
        description="Direction of the call (inbound/outbound)",
        example="outbound"
    )
    status: str = Field(
        ..., 
        description="Current status of the call",
        example="completed"
    )
    start_time: str = Field(
        ..., 
        description="Start time of the call in ISO format",
        example="2025-03-23T10:00:00Z"
    )
    duration: int = Field(
        ..., 
        ge=0, 
        description="Duration of the call in seconds",
        example=300
    )
    outcome: str = Field(
        ..., 
        description="Outcome of the call",
        example="appointment_booked"
    )
    sentiment: str = Field(
        ..., 
        description="Detected sentiment of the call",
        example="positive"
    )
    summary: str = Field(
        ..., 
        description="Summary of the call conversation",
        example="Customer inquired about membership options and booked a consultation appointment."
    )
    
    @validator('direction')
    def validate_direction(cls, v):
        try:
            return CallDirection(v).value
        except ValueError:
            raise ValueError(f'Direction must be one of: {[d.value for d in CallDirection]}')
            
    @validator('status')
    def validate_status(cls, v):
        try:
            return CallStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[s.value for s in CallStatus]}')
            
    @validator('outcome')
    def validate_outcome(cls, v):
        try:
            return CallOutcome(v).value
        except ValueError:
            raise ValueError(f'Outcome must be one of: {[o.value for o in CallOutcome]}')
    
    @validator('sentiment')
    def validate_sentiment(cls, v):
        try:
            return CallSentiment(v).value
        except ValueError:
            raise ValueError(f'Sentiment must be one of: {[s.value for s in CallSentiment]}')
    
    class Config:
        use_enum_values = True
        schema_extra = {
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
        }

class Appointment(BaseModel):
    id: str = Field(..., description="Unique identifier for the appointment")
    type: str = Field(
        ..., 
        description="Type of the appointment",
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
        description="Duration of the appointment in minutes",
        example=60
    )
    status: str = Field(
        ..., 
        description="Current status of the appointment",
        example="scheduled"
    )
    branch_name: str = Field(
        ..., 
        description="Name of the branch where the appointment is scheduled",
        example="Downtown Fitness Center"
    )
    
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
        schema_extra = {
            "example": {
                "id": "appt-456",
                "type": "consultation",
                "date": "2025-03-25T14:00:00Z",
                "duration": 60,
                "status": "scheduled",
                "branch_name": "Downtown Fitness Center"
            }
        }