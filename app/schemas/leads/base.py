from pydantic import BaseModel
from typing import Optional, List
from app.schemas.common.lead_types import Tag

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    status: str
    notes: Optional[str] = None
    interest: Optional[str] = None
    interest_location: Optional[str] = None
    branch_id: str
    source: str

class LeadCreate(LeadBase):
    tags: List[str] = []

class LeadUpdate(LeadBase):
    pass

class LeadStatusUpdate(BaseModel):
    status: str 