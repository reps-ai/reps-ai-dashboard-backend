from fastapi import APIRouter
from .login import router as login_router
from .users import router as users_router

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

router.include_router(login_router)
router.include_router(users_router, prefix="/users")