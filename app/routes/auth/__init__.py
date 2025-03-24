from fastapi import APIRouter
from app.routes.auth import login, user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Include subrouters
router.include_router(login.router)
router.include_router(user.router) 