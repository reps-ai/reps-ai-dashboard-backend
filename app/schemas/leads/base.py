from pydantic import field_validator, ConfigDict, BaseModel, Field, EmailStr
from typing import Optional, List, Union
from app.schemas.common.lead_types import Tag, LeadStatus, LeadSource
import re
import uuid

class LeadBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, 
                          description="Lead's first name", examples=["John"])
    last_name: str = Field(..., min_length=1, max_length=50, 
                         description="Lead's last name", examples=["Doe"])
    phone: str = Field(..., description="Lead's phone number", examples=["+1234567890"])
    email: Optional[EmailStr] = Field(None, description="Lead's email address", 
                                   examples=["john.doe@example.com"])
    status: str = Field(..., description="Current status of the lead", examples=["new"])
    notes: Optional[str] = Field(None, description="Additional notes about the lead")
    interest: Optional[str] = Field(None, description="Lead's area of interest", 
                                 examples=["Personal Training"])
    interest_location: Optional[str] = Field(None, description="Preferred gym location")
    source: str = Field(..., description="Source of the lead", examples=["website"])
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Simplified phone validation - should match country-specific patterns in production
        if not re.match(r'^\+?[0-9\-\(\)\s]{8,20}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        try:
            return LeadStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[status.value for status in LeadStatus]}')
    
    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        try:
            return LeadSource(v).value
        except ValueError:
            raise ValueError(f'Source must be one of: {[source.value for source in LeadSource]}')
    model_config = ConfigDict(use_enum_values=True)

class LeadCreate(LeadBase):
    tags: List[uuid.UUID] = Field(default_factory=list, description="List of tag IDs to associate with the lead")

# For route input, we need a schema without branch_id which will be added from dependency
class LeadCreateInput(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, 
                          description="Lead's first name", examples=["John"])
    last_name: str = Field(..., min_length=1, max_length=50, 
                         description="Lead's last name", examples=["Doe"])
    phone: str = Field(..., description="Lead's phone number", examples=["+1234567890"])
    email: Optional[EmailStr] = Field(None, description="Lead's email address", 
                                   examples=["john.doe@example.com"])
    status: str = Field(..., description="Current status of the lead", examples=["new"])
    notes: Optional[str] = Field(None, description="Additional notes about the lead")
    interest: Optional[str] = Field(None, description="Lead's area of interest", 
                                 examples=["Personal Training"])
    interest_location: Optional[str] = Field(None, description="Preferred gym location")
    source: str = Field(..., description="Source of the lead", examples=["website"])
    tags: List[uuid.UUID] = Field(default_factory=list, description="List of tag IDs to associate with the lead")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Simplified phone validation - should match country-specific patterns in production
        if not re.match(r'^\+?[0-9\-\(\)\s]{8,20}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        try:
            return LeadStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[status.value for status in LeadStatus]}')
    
    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        try:
            return LeadSource(v).value
        except ValueError:
            raise ValueError(f'Source must be one of: {[source.value for source in LeadSource]}')
    model_config = ConfigDict(use_enum_values=True)

class LeadUpdate(LeadBase):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, 
                                  description="Lead's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, 
                                 description="Lead's last name")
    phone: Optional[str] = Field(None, description="Lead's phone number")
    status: Optional[str] = Field(None, description="Current status of the lead")
    branch_id: Optional[uuid.UUID] = Field(None, description="ID of the branch")
    source: Optional[str] = Field(None, description="Source of the lead")
    
    # Validators are inherited from LeadBase

class LeadStatusUpdate(BaseModel):
    status: str = Field(
        ..., 
        description="New status for the lead",
        examples=["qualified"]
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        try:
            return LeadStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[status.value for status in LeadStatus]}')
    model_config = ConfigDict(use_enum_values=True)