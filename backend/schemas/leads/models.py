from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from enum import Enum
from ..common.base import TimestampMixin

class LeadSource(str, Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    DIRECT = "direct"
    SOCIAL = "social"
    OTHER = "other"

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"

class LeadBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: str
    status: LeadStatus = LeadStatus.NEW
    source: LeadSource = LeadSource.OTHER
    branch_id: str
    qualification_score: Optional[float] = Field(None, ge=0, le=1)
    notes: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        cleaned = ''.join(filter(str.isdigit, v))
        if not (10 <= len(cleaned) <= 15):
            raise ValueError('Phone number must be between 10 and 15 digits')
        return v

class LeadCreate(LeadBase):
    """Request model for creating new leads"""
    model_config = ConfigDict(from_attributes=True)

class LeadUpdate(BaseModel):
    """Request model for updating existing leads"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    qualification_score: Optional[float] = None
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class LeadInDB(LeadBase, TimestampMixin):
    """Database model representation"""
    id: str
    last_contacted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)