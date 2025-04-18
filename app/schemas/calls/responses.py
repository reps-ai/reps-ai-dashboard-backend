from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import field_validator, model_validator, ConfigDict, BaseModel, Field
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome, CallSentiment, TranscriptEntry
import uuid
import json
import ast
from backend.utils.helpers.transcript_parser import parse_transcript_block

class LeadSummary(BaseModel):
    id: str = Field(..., description="Unique identifier for the lead")
    first_name: str = Field(..., description="First name of the lead")
    last_name: str = Field(..., description="Last name of the lead")
    phone: str = Field(..., description="Phone number of the lead")
    email: Optional[str] = Field(None, description="Email address of the lead")
    
    @field_validator('id', mode="before")
    @classmethod
    def convert_id_to_str(cls, v):
        """Convert UUID or other types to string"""
        return str(v) if v is not None else None
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "lead-123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "email": "john.doe@example.com"
        }
    })

class CallResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the call")
    lead_id: str = Field(..., description="ID of the lead associated with this call")
    lead: LeadSummary = Field(..., description="Summary information about the lead")
    direction: str = Field(default="outbound", description="Direction of the call (inbound/outbound)")  # Default added
    status: str = Field(default="scheduled", description="Current status of the call")  # Default added
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
    
    # Add validators to handle type conversions
    @field_validator('id', 'lead_id', 'campaign_id', mode="before")
    @classmethod
    def convert_ids_to_str(cls, v):
        """Convert UUID or other types to string"""
        return str(v) if v is not None else None
    
    @field_validator('start_time', 'end_time', 'created_at', mode="before")
    @classmethod
    def convert_datetime_to_str(cls, v):
        """Handle datetime conversion to ISO format string"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        if isinstance(v, str):
            return v
        # For any other type, convert to string
        return str(v)
    
    @field_validator('direction')
    @classmethod
    def validate_direction(cls, v):
        if not v:  # Handle None or empty string
            return "outbound"  # Default value
        try:
            return CallDirection(v).value
        except ValueError:
            # More permissive - if not a valid enum, just return as is
            return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if not v:  # Handle None or empty string
            return "scheduled"  # Default value
        try:
            return CallStatus(v).value
        except ValueError:
            # More permissive - if not a valid enum, just return as is
            return v
    
    @field_validator('outcome')
    @classmethod
    def validate_outcome(cls, v):
        if v is None:
            return None
        try:
            return CallOutcome(v).value
        except ValueError:
            # More permissive - if not a valid enum, just return as is
            return v
    
    @field_validator('sentiment')
    @classmethod
    def validate_sentiment(cls, v):
        if v is None:
            return None
        try:
            return CallSentiment(v).value
        except ValueError:
            # More permissive - if not a valid enum, just return as is
            return v
    
    # Add a root validator to handle missing fields or inconsistent data
    @model_validator(mode="before")
    @classmethod
    def ensure_required_fields(cls, values):
        """Ensure all required fields have values, even if they're not in the input."""
        # Make sure 'lead' is populated
        if 'lead' not in values or not values['lead']:
            if 'lead_id' in values:
                # Create a minimal lead object based on lead_id
                values['lead'] = {'id': values['lead_id'], 'first_name': '', 'last_name': '', 'phone': ''}
        return values
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
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
    })

class CallDetailResponse(CallResponse):
    transcript: Optional[List[TranscriptEntry]] = Field(
        None, 
        description="Transcript of the call conversation with speaker identification"
    )
    metrics: Optional[Dict[str, float]] = Field(None, description="Call metrics and analysis")
    
    @field_validator('transcript', mode="before")
    @classmethod
    def validate_transcript(cls, v):
        """
        Normalize transcript field: parse JSON strings into lists, wrap plain text,
        and otherwise ensure we return a list or None.
        """
        if v is None:
            return None
        # Try parsing if transcript was stored as a JSON string
        if isinstance(v, str):
            # First, attempt JSON decoding
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            # Next, attempt Python literal eval (for repr strings)
            try:
                parsed = ast.literal_eval(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            # Fallback: parse block into utterances if possible
            parsed = parse_transcript_block(v)
            if parsed:
                return parsed
            # If parsing fails, wrap as a single system message
            return [{"speaker": "system", "text": v, "timestamp": 0.0}]
        # If already a list, return as-is
        if isinstance(v, list):
            return v
        # Unrecognized format
        return None
    model_config = ConfigDict(json_schema_extra={
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
    })

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
    page_size: int = Field(..., ge=1, description="Number of calls per page")
    pages: int = Field(1, ge=1, description="Total number of pages available")  # Set default to 1
    
    @field_validator('pages', mode="before")
    @classmethod
    def ensure_min_pages(cls, v):
        """Ensure pages is at least 1 even when there are no results"""
        if v is None or v < 1:
            return 1
        return v
    
    # Add a root validator to ensure consistency between total and pages
    @model_validator(mode="before")
    @classmethod
    def calculate_pages_if_missing(cls, values):
        """Calculate pages from total and page_size if not provided"""
        if 'total' in values and 'page_size' in values and values['page_size'] > 0:
            # Calculate pages but ensure it's at least 1
            calculated_pages = max(1, (values['total'] + values['page_size'] - 1) // values['page_size'])
            # Only set if pages is missing or invalid
            if 'pages' not in values or values['pages'] is None or values['pages'] < 1:
                values['pages'] = calculated_pages
        return values

class CallListResponse(BaseModel):
    calls: List[CallResponse] = Field(
        default_factory=list,  # Default to empty list
        description="List of call data. May be empty if no calls match the filter criteria."
    )
    pagination: PaginationInfo = Field(..., description="Pagination information")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "calls": [
                # Example call data
            ],
            "pagination": {
                "total": 0,
                "page": 1,
                "page_size": 10,
                "pages": 1
            }
        }
    })