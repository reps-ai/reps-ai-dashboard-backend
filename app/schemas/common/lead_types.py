from enum import Enum
from pydantic import field_validator, ConfigDict, BaseModel, Field
from typing import Optional, List

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
    id: str = Field(..., min_length=1, description="Unique identifier for the tag")
    name: str = Field(..., min_length=1, description="Name of the tag")
    color: str = Field(..., description="Color code for the tag (e.g., #RRGGBB)")
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        # Simplified color validation for robust testing
        if not v.startswith('#'):
            raise ValueError('Color must start with #')
        try:
            # Try to parse the hex value
            if len(v) == 7:  # #RRGGBB format
                int(v[1:], 16)
            else:
                raise ValueError('Color must be in #RRGGBB format')
        except ValueError:
            raise ValueError('Color must be a valid hex color code (e.g., #RRGGBB)')
        return v
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "tag-123",
            "name": "VIP",
            "color": "#FF5733"
        }
    })

class AssignedStaff(BaseModel):
    id: str = Field(..., min_length=1, description="Unique identifier for the staff member")
    first_name: str = Field(..., min_length=1, description="First name of the staff member")
    last_name: str = Field(..., min_length=1, description="Last name of the staff member")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "staff-123",
            "first_name": "John",
            "last_name": "Doe"
        }
    })