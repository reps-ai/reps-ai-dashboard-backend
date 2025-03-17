from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    branch_id: Optional[str] = None
    script_id: Optional[str] = None

class CampaignCreate(CampaignBase):
    lead_ids: List[str]
    scheduled_start: Optional[str] = None
    max_concurrent_calls: Optional[int] = 5

class CampaignResponse(CampaignBase):
    id: str
    status: str
    total_leads: int
    completed_calls: int
    successful_calls: int
    created_at: str
    updated_at: str

class CampaignDetailResponse(CampaignResponse):
    leads: List[str]
    calls: List[str] 