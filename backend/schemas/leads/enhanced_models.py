from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from ..common.base import TimestampMixin
from ..common.enums import LeadSource, LeadStatus
from ..common.validators import PhoneValidator, ScoreValidator, EmailValidator

class LeadContact(BaseModel, EmailValidator, PhoneValidator):
    email: Optional[EmailStr] = None
    phone: str = Field(..., description="Primary contact number")
    alternate_phone: Optional[str] = Field(None, description="Alternative contact number")
    preferred_contact_method: str = Field("phone", description="Preferred method of contact")
    best_time_to_contact: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class LeadPreferences(BaseModel):
    preferred_location: Optional[str] = None
    budget_range: Optional[str] = None
    membership_interest: Optional[List[str]] = None
    fitness_goals: Optional[List[str]] = None
    availability: Optional[Dict[str, List[str]]] = None
    model_config = ConfigDict(from_attributes=True)

class LeadBase(BaseModel, ScoreValidator):
    first_name: str = Field(..., min_length=1, description="Lead's first name")
    last_name: str = Field(..., min_length=1, description="Lead's last name")
    contact_info: LeadContact
    status: LeadStatus = Field(default=LeadStatus.NEW, description="Current status of the lead")
    source: LeadSource = Field(default=LeadSource.OTHER, description="Source of the lead")
    branch_id: str = Field(..., description="ID of the associated branch")
    qualification_score: Optional[float] = Field(None, ge=0, le=1, description="Lead qualification score")
    preferences: Optional[LeadPreferences] = None
    notes: Optional[str] = Field(None, description="Additional notes about the lead")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the lead")
    model_config = ConfigDict(from_attributes=True)

class LeadActivity(BaseModel):
    activity_type: str
    timestamp: datetime
    description: str
    performed_by: str
    related_entity_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class LeadCreate(LeadBase):
    """Request model for creating new leads"""
    pass

class LeadUpdate(BaseModel):
    """Request model for updating existing leads"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_info: Optional[LeadContact] = None
    status: Optional[LeadStatus] = None
    qualification_score: Optional[float] = Field(None, ge=0, le=1)
    preferences: Optional[LeadPreferences] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)

class LeadInDB(LeadBase, TimestampMixin):
    """Database model representation"""
    id: str
    last_contacted_at: Optional[datetime] = None
    activities: List[LeadActivity] = Field(default_factory=list)
    total_interactions: int = Field(default=0)
    model_config = ConfigDict(from_attributes=True)

class LeadAnalytics(BaseModel):
    total_leads: int = Field(..., description="Total number of leads")
    qualified_leads: int = Field(..., description="Number of qualified leads")
    conversion_rate: float = Field(..., ge=0, le=1, description="Lead conversion rate")
    average_qualification_score: float = Field(..., ge=0, le=1, description="Average qualification score")
    leads_by_status: Dict[LeadStatus, int] = Field(..., description="Lead distribution by status")
    leads_by_source: Dict[LeadSource, int] = Field(..., description="Lead distribution by source")
    response_time_metrics: Dict[str, float] = Field(..., description="Response time metrics")
    model_config = ConfigDict(from_attributes=True)
