from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class CallStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VOICEMAIL = "voicemail"
    MISSED = "missed"

class CallOutcome(str, Enum):
    APPOINTMENT_BOOKED = "appointment_booked"
    CALLBACK_REQUESTED = "callback_requested"
    NOT_INTERESTED = "not_interested"
    UNDECIDED = "undecided"
    NO_ANSWER = "no_answer"
    WRONG_NUMBER = "wrong_number"
    LEFT_MESSAGE = "left_message"
    INFORMATION_PROVIDED = "information_provided"

class CallSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class TranscriptEntry(BaseModel):
    speaker: str = Field(
        ..., 
        description="Speaker identifier (agent or customer)",
        example="agent"
    )
    text: str = Field(
        ..., 
        description="Text spoken by the speaker",
        example="How can I help you today?"
    )
    timestamp: float = Field(
        ..., 
        ge=0.0, 
        description="Timestamp in seconds from the start of the call",
        example=10.5
    )
    
    @validator('speaker')
    def validate_speaker(cls, v):
        if v.lower() not in ["agent", "customer", "system"]:
            raise ValueError("Speaker must be 'agent', 'customer', or 'system'")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "speaker": "agent",
                "text": "How can I help you today?",
                "timestamp": 10.5
            }
        }