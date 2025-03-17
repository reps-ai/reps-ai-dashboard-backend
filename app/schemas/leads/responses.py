from typing import List, Optional
from app.schemas.leads.base import LeadBase
from app.schemas.common.lead_types import Tag, AssignedTo
from app.schemas.common.activity import Call, Appointment
from pydantic import BaseModel

class LeadResponse(LeadBase):
    id: str
    branch_name: str
    last_conversation_summary: Optional[str] = None
    last_called: Optional[str] = None
    created_at: str
    updated_at: str
    score: float
    call_count: int
    appointment_date: Optional[str] = None
    tags: List[Tag] = []

class LeadDetailResponse(LeadResponse):
    assigned_to: Optional[AssignedTo] = None
    calls: List[Call] = []
    appointments: List[Appointment] = []

class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    pages: int

class LeadListResponse(BaseModel):
    data: List[LeadResponse]
    pagination: PaginationInfo 