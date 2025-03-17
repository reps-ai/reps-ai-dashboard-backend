from enum import Enum
from pydantic import BaseModel
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
    id: str
    name: str
    color: str

class AssignedTo(BaseModel):
    id: str
    first_name: str
    last_name: str 