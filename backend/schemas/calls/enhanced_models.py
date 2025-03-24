from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from ..common.base import TimestampMixin
from ..common.enums import CallStatus, CallOutcome, SentimentCategory

class CallMetadata(BaseModel):
    call_id: str = Field(..., description="Unique identifier for the call")
    recording_url: Optional[str] = Field(None, description="URL to the call recording")
    duration: int = Field(..., description="Call duration in seconds")
    connection_quality: Optional[float] = Field(None, ge=0, le=1, description="Call connection quality score")
    model_config = ConfigDict(from_attributes=True)

class CallTranscript(BaseModel):
    timestamp: datetime
    speaker: str
    text: str
    confidence: float = Field(..., ge=0, le=1)
    sentiment: Optional[float] = Field(None, ge=-1, le=1)
    model_config = ConfigDict(from_attributes=True)

class CallAnalysis(BaseModel):
    sentiment_score: float = Field(..., ge=-1, le=1, description="Overall call sentiment score")
    sentiment_category: SentimentCategory
    key_topics: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    follow_up_needed: bool = False
    follow_up_reason: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CallBase(BaseModel):
    lead_id: str = Field(..., description="ID of the associated lead")
    agent_id: str = Field(..., description="ID of the assigned agent")
    scheduled_time: datetime
    expected_duration: int = Field(..., description="Expected duration in minutes")
    status: CallStatus = Field(default=CallStatus.SCHEDULED)
    priority: int = Field(default=1, ge=1, le=5, description="Call priority (1-5)")
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CallCreate(CallBase):
    """Request model for creating new calls"""
    pass

class CallUpdate(BaseModel):
    """Request model for updating existing calls"""
    status: Optional[CallStatus] = None
    outcome: Optional[CallOutcome] = None
    actual_duration: Optional[int] = None
    notes: Optional[str] = None
    analysis: Optional[CallAnalysis] = None
    model_config = ConfigDict(from_attributes=True)

class CallInDB(CallBase, TimestampMixin):
    """Database model representation"""
    id: str
    metadata: Optional[CallMetadata] = None
    transcript: Optional[List[CallTranscript]] = None
    analysis: Optional[CallAnalysis] = None
    completed_at: Optional[datetime] = None
    outcome: Optional[CallOutcome] = None
    model_config = ConfigDict(from_attributes=True)

class CallAnalytics(BaseModel):
    total_calls: int = Field(..., description="Total number of calls")
    completed_calls: int = Field(..., description="Number of completed calls")
    average_duration: float = Field(..., description="Average call duration in minutes")
    sentiment_distribution: Dict[SentimentCategory, int] = Field(..., description="Distribution of call sentiments")
    completion_rate: float = Field(..., ge=0, le=1, description="Call completion rate")
    calls_by_status: Dict[CallStatus, int] = Field(..., description="Call distribution by status")
    average_response_time: float = Field(..., description="Average response time in minutes")
    peak_call_times: Dict[str, int] = Field(..., description="Distribution of calls by time of day")
    model_config = ConfigDict(from_attributes=True)
