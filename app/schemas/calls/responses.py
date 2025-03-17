from pydantic import BaseModel
from typing import List, Optional
from app.schemas.common.call_types import TranscriptEntry
from datetime import datetime

class LeadSummary(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    status: Optional[str] = None

class CallResponse(BaseModel):
    id: str
    lead_id: str
    lead: LeadSummary
    direction: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    summary: Optional[str] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    notes: Optional[str] = None
    campaign_id: Optional[str] = None
    created_at: str

class CallDetailResponse(CallResponse):
    transcript: Optional[str] = None
    agent_id: Optional[str] = None
    campaign_name: Optional[str] = None
    updated_at: str

class CallTranscriptResponse(BaseModel):
    id: str
    transcript: List[TranscriptEntry]
    duration: int

class CallNoteResponse(BaseModel):
    id: str
    call_id: str
    content: str
    created_at: str
    created_by: str

class CallOutcomeResponse(BaseModel):
    id: str
    outcome: str
    updated_at: str

class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    pages: int

class CallListResponse(BaseModel):
    data: List[CallResponse]
    pagination: PaginationInfo 