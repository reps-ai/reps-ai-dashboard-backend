from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional

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

class Tag(BaseModel):
    id: str = Field(..., description="Unique identifier for the tag")
    name: str = Field(..., description="Name of the tag")
    color: str = Field(..., description="Color code for the tag (e.g., #RRGGBB)")
    
    @validator('color')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color code (e.g., #RRGGBB)')
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError('Color must be a valid hex color code (e.g., #RRGGBB)')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "tag-123",
                "name": "VIP",
                "color": "#FF5733"
            }
        }

class AssignedTo(BaseModel):
    id: str = Field(..., description="Unique identifier for the staff member")
    first_name: str = Field(..., description="First name of the staff member")
    last_name: str = Field(..., description="Last name of the staff member")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "staff-123",
                "first_name": "John",
                "last_name": "Doe"
            }
        }