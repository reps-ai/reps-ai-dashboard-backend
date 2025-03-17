from enum import Enum
from pydantic import BaseModel
from typing import Optional

class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class CallStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    MISSED = "missed"
    CANCELED = "canceled"

class CallOutcome(str, Enum):
    APPOINTMENT_BOOKED = "appointment_booked"
    FOLLOW_UP_NEEDED = "follow_up_needed"
    NOT_INTERESTED = "not_interested"
    WRONG_NUMBER = "wrong_number"
    VOICEMAIL = "voicemail"
    NO_ANSWER = "no_answer"
    OTHER = "other"

class CallSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class TranscriptEntry(BaseModel):
    speaker: str
    text: str
    timestamp: float 