from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome, CallSentiment, TranscriptEntry

class LeadSummary(BaseModel):
    id: str = Field(..., description="Unique identifier for the lead")
    first_name: str = Field(..., description="First name of the lead")
    last_name: str = Field(..., description="Last name of the lead")
    phone: str = Field(..., description="Phone number of the lead")
    email: Optional[str] = Field(None, description="Email address of the lead")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "lead-123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "email": "john.doe@example.com"
            }
        }

class CallResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the call")
    lead_id: str = Field(..., description="ID of the lead associated with this call")
    lead: LeadSummary = Field(..., description="Summary information about the lead")
    direction: str = Field(..., description="Direction of the call (inbound/outbound)")
    status: str = Field(..., description="Current status of the call")
    start_time: Optional[str] = Field(None, description="Start time of the call in ISO format")
    end_time: Optional[str] = Field(None, description="End time of the call in ISO format")
    duration: Optional[int] = Field(None, ge=0, description="Duration of the call in seconds")
    outcome: Optional[str] = Field(None, description="Outcome of the call")
    notes: Optional[str] = Field(None, description="Additional notes about the call")
    summary: Optional[str] = Field(None, description="Summary of the call conversation")
    sentiment: Optional[str] = Field(None, description="Detected sentiment of the call")
    recording_url: Optional[str] = Field(None, description="URL to the call recording, if available")
    created_at: str = Field(..., description="Creation timestamp in ISO format")
    campaign_id: Optional[str] = Field(None, description="ID of the campaign this call is part of")
    campaign_name: Optional[str] = Field(None, description="Name of the campaign")
    
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
        if v is not None:
            try:
                return CallOutcome(v).value
            except ValueError:
                raise ValueError(f'Outcome must be one of: {[o.value for o in CallOutcome]}')
        return v
    
    @validator('sentiment')
    def validate_sentiment(cls, v):
        if v is not None:
            try:
                return CallSentiment(v).value
            except ValueError:
                raise ValueError(f'Sentiment must be one of: {[s.value for s in CallSentiment]}')
        return v
    
    @validator('start_time', 'end_time', 'created_at')
    def validate_timestamps(cls, v):
        if v is not None:
            try:
                # Parse the datetime to validate format
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Timestamp must be a valid ISO datetime format')
        return v
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": "call-123",
                "lead_id": "lead-456",
                "lead": {
                    "id": "lead-456",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1234567890",
                    "email": "john.doe@example.com"
                },
                "direction": "outbound",
                "status": "completed",
                "start_time": "2025-03-23T10:00:00Z",
                "end_time": "2025-03-23T10:05:00Z",
                "duration": 300,
                "outcome": "appointment_booked",
                "sentiment": "positive",
                "summary": "Customer showed interest in premium membership and scheduled a visit",
                "created_at": "2025-03-23T09:30:00Z"
            }
        }

class CallDetailResponse(CallResponse):
    transcript: Optional[List[TranscriptEntry]] = Field(
        None, 
        description="Transcript of the call conversation with speaker identification"
    )
    metrics: Optional[Dict[str, float]] = Field(None, description="Call metrics and analysis")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "call-123",
                "lead_id": "lead-456",
                "lead": {
                    "id": "lead-456",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1234567890",
                    "email": "john.doe@example.com"
                },
                "direction": "outbound",
                "status": "completed",
                "start_time": "2025-03-23T10:00:00Z",
                "end_time": "2025-03-23T10:05:00Z",
                "duration": 300,
                "outcome": "appointment_booked",
                "sentiment": "positive",
                "summary": "Customer showed interest in premium membership and scheduled a visit",
                "created_at": "2025-03-23T09:30:00Z",
                "transcript": [
                    {"speaker": "agent", "text": "Hello, this is Fitness Gym calling. How are you today?", "timestamp": 0.0},
                    {"speaker": "customer", "text": "I'm good, thanks for asking.", "timestamp": 3.5}
                ],
                "metrics": {
                    "talk_ratio": 0.6,
                    "interruptions": 0,
                    "talk_speed": 145.2
                }
            }
        }

class CallTranscriptResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the call transcript")
    transcript: List[TranscriptEntry] = Field(..., description="Transcript of the call conversation with speaker identification")
    duration: int = Field(..., ge=0, description="Duration of the call in seconds")

class CallNoteResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the call note")
    call_id: str = Field(..., description="ID of the call associated with this note")
    content: str = Field(..., description="Content of the note")
    created_at: str = Field(..., description="Creation timestamp in ISO format")
    created_by: str = Field(..., description="User who created the note")

class CallOutcomeResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the call outcome")
    outcome: str = Field(..., description="Outcome of the call")
    updated_at: str = Field(..., description="Last updated timestamp in ISO format")

class PaginationInfo(BaseModel):
    total: int = Field(..., ge=0, description="Total number of calls available")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Number of calls per page")
    pages: int = Field(..., ge=1, description="Total number of pages available")

class CallListResponse(BaseModel):
    data: List[CallResponse] = Field(..., description="List of call data")
    pagination: PaginationInfo = Field(..., description="Pagination information")