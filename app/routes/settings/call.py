from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/call")
async def get_call_settings(current_user = Depends(get_current_user)):
    """
    Get call handling settings (hours, forwarding, etc.).
    """
    # TODO: Implement call settings retrieval logic
    return {"message": "Get call settings endpoint"}

@router.put("/call")
async def update_call_settings(current_user = Depends(get_admin_user)):
    """
    Update call handling settings.
    """
    # TODO: Implement call settings update logic
    return {"message": "Update call settings endpoint"} 