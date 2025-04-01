"""
Authentication schemas for the API.
"""
from pydantic import BaseModel, EmailStr, Field
import uuid
from typing import Optional, Literal

class UserCreate(BaseModel):
    """Schema for user creation"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=1)
    branch_id: uuid.UUID
    role: Literal["admin", "manager", "agent"] = "agent"
    username: Optional[str] = None  # Optional username field - will be generated if not provided
