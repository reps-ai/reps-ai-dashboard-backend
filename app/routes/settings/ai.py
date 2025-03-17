from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/ai")
async def get_ai_settings(current_user = Depends(get_current_user)):
    """
    Get the AI agent behavior settings.
    """
    # TODO: Implement AI settings retrieval logic
    return {"message": "Get AI settings endpoint"}

@router.put("/ai")
async def update_ai_settings(current_user = Depends(get_admin_user)):
    """
    Update the AI agent behavior settings.
    """
    # TODO: Implement AI settings update logic
    return {"message": "Update AI settings endpoint"} 