from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
import uuid

from app.dependencies import get_current_user, User
from app.auth.oauth2 import create_access_token, verify_access_token
from backend.db.connections.database import get_db
from backend.db.models.user import User as DBUser
from backend.utils.logging.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenResponse:
    """Token response model"""
    def __init__(self, access_token: str, token_type: str):
        self.access_token = access_token
        self.token_type = token_type

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Authenticate a user and return JWT tokens.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        session: Database session
        
    Returns:
        JWT token if authentication is successful
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    
    # Query user by email (username field contains the email)
    query = select(DBUser).where(DBUser.email == form_data.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"Failed login: User {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password - in production, you'd check the hashed password
    # This is a simplified example, in real app use proper password verification:
    # is_valid = pwd_context.verify(form_data.password, user.password)
    
    # CRITICAL SECURITY ISSUE: Plain text password comparison
    # is_valid = form_data.password == user.password
    
    # Should be replaced with proper hashing:
    is_valid = pwd_context.verify(form_data.password, user.password)
    
    if not is_valid:
        logger.warning(f"Failed login: Incorrect password for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token data with user, branch, and gym IDs
    token_data = {
        "user_id": user.id,
        "branch_id": str(user.branch_id) if user.branch_id else None,
        "gym_id": str(user.gym_id) if user.gym_id else None,
        "sub": user.email,  # subject claim
        "is_admin": user.is_admin
    }
    
    # Create access token
    access_token = create_access_token(token_data)
    
    # Return token in the format OAuth2 expects
    logger.info(f"User {user.email} logged in successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.email,
        "is_admin": user.is_admin,
        "branch_id": str(user.branch_id) if user.branch_id else None,
        "gym_id": str(user.gym_id) if user.gym_id else None
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout a user by invalidating their JWT token.
    
    Note: This is a placeholder as JWT tokens can't be directly invalidated once issued.
    In a real application, you might:
    1. Use a token blacklist/database
    2. Keep tokens short-lived and use refresh tokens
    3. Update a user version in the database that's checked during validation
    
    Args:
        current_user: Currently authenticated user
    
    Returns:
        Success message
    """
    # In a real implementation, this would add the token to a blacklist
    # or increment the user's token version in the database
    
    logger.info(f"User {current_user.email} logged out")
    return {"message": "Successfully logged out"}

@router.post("/refresh-token")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh an access token.
    
    Args:
        current_user: Currently authenticated user from token verification
        
    Returns:
        New access token
    """
    # In a real implementation, this would take a refresh token and issue a new access token
    # For simplicity, we're just creating a new access token based on the current user
    
    # Create new token data
    token_data = {
        "user_id": current_user.id,
        "branch_id": str(current_user.branch_id) if current_user.branch_id else None,
        "gym_id": str(current_user.gym_id) if current_user.gym_id else None,
        "sub": current_user.email,
        "is_admin": current_user.is_admin
    }
    
    # Create new access token
    access_token = create_access_token(token_data)
    
    logger.info(f"Generated refreshed token for user {current_user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": current_user.id
    }