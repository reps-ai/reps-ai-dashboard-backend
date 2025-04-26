"""
Response schemas for campaign operations.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import CampaignBase

class CampaignResponse(CampaignBase):
    """Response model for campaign operations."""
    id: str = Field(..., description="ID of the campaign")
    branch_id: str = Field(..., description="ID of the branch")
    campaign_status: str = Field(..., description="Status of the campaign")
    call_count: int = Field(0, description="Number of calls made for this campaign")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metrics: Optional[Dict[str, Any]] = Field({}, description="Campaign metrics")

class CampaignDetailResponse(CampaignResponse):
    """Detailed response model for campaign operations."""
    lead_count: int = Field(0, description="Number of leads in the campaign")
    schedule: Optional[Dict[str, Any]] = Field({}, description="Campaign schedule configuration")

class CampaignListResponse(BaseModel):
    """Response model for listing campaigns."""
    data: List[CampaignResponse] = Field(..., description="List of campaigns")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")

class CampaignScheduleResponse(BaseModel):
    """Response model for scheduling calls."""
    campaign_id: str = Field(..., description="ID of the campaign")
    scheduled_calls: List[Dict[str, Any]] = Field(..., description="List of scheduled calls")
    message: str = Field(..., description="Status message")
