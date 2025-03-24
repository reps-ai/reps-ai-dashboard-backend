from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from ..common.base import TimestampMixin

class CallStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CallOutcome(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class CallBase(BaseModel):
    lead_id: str
    scheduled_time: datetime
    duration: Optional[int] = Field(None, description="Duration in seconds")
    status: CallStatus = CallStatus.SCHEDULED
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CallCreate(CallBase):
    """Request model for creating new calls"""
    pass

class CallUpdate(BaseModel):
    """Request model for updating existing calls"""
    status: Optional[CallStatus] = None
    outcome: Optional[CallOutcome] = None
    duration: Optional[int] = None
    notes: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    model_config = ConfigDict(from_attributes=True)

class CallInDB(CallBase, TimestampMixin):
    """Database model representation"""
    id: str
    completed_at: Optional[datetime] = None
    outcome: Optional[CallOutcome] = None
    sentiment_score: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)