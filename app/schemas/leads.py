from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(str, Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    WALK_IN = "walk_in"
    PHONE = "phone"
    SOCIAL = "social"
    OTHER = "other"


class LeadBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: str
    source: LeadSource = LeadSource.OTHER
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(LeadBase):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None


class LeadStatusUpdate(BaseModel):
    status: LeadStatus
    notes: Optional[str] = None


class LeadNote(BaseModel):
    content: str


class LeadTag(BaseModel):
    id: int
    name: str


class LeadTagCreate(BaseModel):
    name: str


class TimelineEntry(BaseModel):
    id: int
    timestamp: datetime
    action: str
    description: str


class Lead(LeadBase):
    id: int
    status: LeadStatus = LeadStatus.NEW
    created_at: datetime
    updated_at: datetime
    tags: List[LeadTag] = []
    gym_id: int

    class Config:
        orm_mode = True 