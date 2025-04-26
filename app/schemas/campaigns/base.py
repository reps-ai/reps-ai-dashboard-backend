"""
Base schemas for campaign operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CampaignBase(BaseModel):
    """Base campaign model with common fields."""
    name: str = Field(..., description="Name of the campaign")
    description: Optional[str] = Field(None, description="Description of the campaign")
    branch_id: Optional[str] = Field(None, description="ID of the branch")  # Keep as optional
    start_date: Optional[datetime] = Field(None, description="Start date for the campaign")
    end_date: Optional[datetime] = Field(None, description="End date for the campaign")
    frequency: int = Field(..., description="Maximum calls per day", ge=1)
    gap: int = Field(..., description="Gap between retries in days", ge=1)

class CampaignCreate(CampaignBase):
    """Model for creating a new campaign."""
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    frequency: int
    gap: int
    # Add this line:
    metrics: Optional[Dict[str, Any]] = None

class CampaignUpdate(BaseModel):
    """Model for updating an existing campaign."""
    name: Optional[str] = Field(None, description="Name of the campaign")
    description: Optional[str] = Field(None, description="Description of the campaign")
    start_date: Optional[datetime] = Field(None, description="Start date for the campaign")
    end_date: Optional[datetime] = Field(None, description="End date for the campaign")
    frequency: Optional[int] = Field(None, description="Maximum calls per day", ge=1)
    gap: Optional[int] = Field(None, description="Gap between retries in days", ge=1)
    campaign_status: Optional[str] = Field(None, description="Status of the campaign")

class CampaignSchedule(BaseModel):
    """Model for campaign schedule configuration."""
    call_days: List[str] = Field(..., description="Days to make calls (mon, tue, wed, etc.)")
    max_daily_calls: int = Field(5, description="Maximum calls per day", ge=1)
    call_hours_start: Optional[str] = Field(None, description="Start time for calls (e.g., '09:00')")
    call_hours_end: Optional[str] = Field(None, description="End time for calls (e.g., '17:00')")
