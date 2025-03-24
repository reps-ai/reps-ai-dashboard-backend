from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/voice")
async def get_voice_settings(current_user = Depends(get_current_user)):
    """
    Get the AI voice agent voice settings.
    """
    # TODO: Implement voice settings retrieval logic
    return {"message": "Get voice settings endpoint"}

@router.put("/voice")
async def update_voice_settings(current_user = Depends(get_admin_user)):
    """
    Update the AI voice agent voice settings.
    """
    # TODO: Implement voice settings update logic
    return {"message": "Update voice settings endpoint"} 