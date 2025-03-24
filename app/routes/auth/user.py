from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user, User
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool
    gym_id: int = None

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get information about the current authenticated user.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin,
        "gym_id": current_user.gym_id
    } 