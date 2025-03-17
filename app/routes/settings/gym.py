from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/gym")
async def get_gym_settings(current_user = Depends(get_current_user)):
    """
    Get the gym's basic settings (name, location, contact info, etc.).
    """
    # TODO: Implement gym settings retrieval logic
    return {"message": "Get gym settings endpoint"}

@router.put("/gym")
async def update_gym_settings(current_user = Depends(get_admin_user)):
    """
    Update the gym's basic settings.
    """
    # TODO: Implement gym settings update logic
    return {"message": "Update gym settings endpoint"} 