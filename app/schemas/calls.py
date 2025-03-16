from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CallStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    MISSED = "missed"


class CallOutcome(str, Enum):
    APPOINTMENT_BOOKED = "appointment_booked"
    FOLLOW_UP_NEEDED = "follow_up_needed"
    NOT_INTERESTED = "not_interested"
    NO_ANSWER = "no_answer"
    WRONG_NUMBER = "wrong_number"
    OTHER = "other"


class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallBase(BaseModel):
    lead_id: int
    direction: CallDirection
    status: CallStatus = CallStatus.SCHEDULED
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    status: Optional[CallStatus] = None
    notes: Optional[str] = None
    outcome: Optional[CallOutcome] = None


class CallOutcomeUpdate(BaseModel):
    outcome: CallOutcome
    notes: Optional[str] = None


class CallNote(BaseModel):
    content: str


class Call(CallBase):
    id: int
    outcome: Optional[CallOutcome] = None
    duration: Optional[int] = None  # in seconds
    recording_url: Optional[str] = None
    transcript_id: Optional[int] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    gym_id: int

    class Config:
        orm_mode = True


class CallCampaign(BaseModel):
    name: str
    lead_ids: List[int]
    message_template: str
    scheduled_start: datetime 