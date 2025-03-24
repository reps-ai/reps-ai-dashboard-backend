from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Get information about the current authenticated user.
    """
    # TODO: Implement user info retrieval
    return {"message": "Current user info endpoint"} 