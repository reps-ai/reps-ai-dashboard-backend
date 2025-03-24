from fastapi import APIRouter, Depends, Body
from app.dependencies import get_current_user

from app.schemas.calls.campaign import CampaignCreate, CampaignResponse

router = APIRouter()

@router.post("/campaign", response_model=CampaignResponse)
async def create_call_campaign(
    campaign: CampaignCreate = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Create a campaign to make outbound calls to multiple leads.
    """
    # Implementation will be added later
    pass 