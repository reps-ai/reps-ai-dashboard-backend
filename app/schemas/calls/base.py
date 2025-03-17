from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common.call_types import CallDirection, CallStatus, CallOutcome

class CallBase(BaseModel):
    lead_id: str
    direction: str
    notes: Optional[str] = None
    campaign_id: Optional[str] = None

class CallCreate(CallBase):
    scheduled_time: Optional[str] = None

class CallUpdate(BaseModel):
    outcome: Optional[str] = None
    notes: Optional[str] = None
    summary: Optional[str] = None

class CallNoteCreate(BaseModel):
    content: str

class CallOutcomeUpdate(BaseModel):
    outcome: str 