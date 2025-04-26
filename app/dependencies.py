from fastapi import Depends, HTTPException, logger, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import os
import logging


# Import the necessary service and repository
from backend.services.call.implementation import DefaultCallService
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.db.connections.database import get_db
from backend.services.call.factory import create_call_service

from backend.services.lead.implementation import DefaultLeadService
from backend.db.repositories.lead.implementations import PostgresLeadRepository

from backend.services.campaign.factory import create_campaign_service_async
from backend.services.campaign.implementation import DefaultCampaignService

# Add logger for better error handling
logger = logging.getLogger(__name__)

# OAuth2 setup - will be used by oauth2.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

# User model expanded to include branch_id
class User(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: str
    gym_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None

    @property
    def is_admin(self) -> bool:
        """Computed property that returns True if user has admin role"""
        return self.role.lower() == "admin"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

# Mock Gym model
class Gym(BaseModel):
    id: uuid.UUID
    name: str
    # Add other gym fields as needed

# Mock Branch model
class Branch(BaseModel):
    id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    # Add other branch fields as needed

# This is a placeholder - in a real app, get these from environment variables
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Get testing mode from environment variable (defaults to False)
TESTING_MODE = os.environ.get("TESTING_MODE", "").lower() == "true"

# Create mock objects for testing
MOCK_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")  # Valid UUID
MOCK_GYM_ID = uuid.UUID("facd154c-9be8-40fb-995f-27ea665d3a8b")  # Valid gym ID
MOCK_BRANCH_ID = uuid.UUID("8d8808a4-22f8-4af3-aec4-bab5b44b1aa7")  # Valid branch ID

# NOTE: The actual authentication functions are now in app/auth/oauth2.py
# These functions remain as fallbacks for testing without authentication

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Get the current authenticated user or return a mock user in testing mode.
    Will raise an authentication error if no token is provided and not in testing mode.
    """
    # Import the real authentication at runtime to avoid circular imports
    from .auth.oauth2 import get_current_user as oauth2_get_current_user
    
    # Special case for testing mode
    if TESTING_MODE:
        logger.debug("Using testing mode authentication")
        return User(
            id=MOCK_USER_ID,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="admin",
            gym_id=MOCK_GYM_ID,
            branch_id=MOCK_BRANCH_ID
        )
    
    # For non-testing mode, we require a token
    if not token:
        logger.warning("Authentication attempt without token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # If a token is provided, use the real authentication
    return await oauth2_get_current_user(token=token, session=db)

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    TESTING MODE: Always returns an admin user.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return current_user

async def get_current_gym(current_user: User = Depends(get_current_user)) -> Gym:
    """
    TESTING MODE: Always returns a mock gym without checking user association.
    
    In testing mode, this will accept any gym ID to allow accessing data across gyms.
    """
    # For testing, return a mock gym without verification
    return Gym(
        id=current_user.gym_id or MOCK_GYM_ID,
        name="Test Gym"
    )

async def get_current_branch(
    branch_id: Optional[Union[uuid.UUID, int, str]] = None,
    current_user: User = Depends(get_current_user)
) -> Branch:
    """
    TESTING MODE: Always returns a mock branch without verifying ownership.
    """
    # Use branch_id from request parameter or from current user if not specified
    branch_uuid = None
    if branch_id:
        branch_uuid = branch_id if isinstance(branch_id, uuid.UUID) else uuid.UUID(str(branch_id))
    else:
        branch_uuid = current_user.branch_id or MOCK_BRANCH_ID
        
    # For testing, return a mock branch
    return Branch(
        id=branch_uuid,
        gym_id=current_user.gym_id or MOCK_GYM_ID,
        name="Test Branch"
    )

# Service dependencies remain unchanged
async def get_call_service(db: AsyncSession = Depends(get_db)) -> DefaultCallService:
    """
    Dependency to get the call service instance with properly initialized repository.
    """
    call_repository = PostgresCallRepository(db)
    return create_call_service(call_repository=call_repository)

async def get_lead_service(db: AsyncSession = Depends(get_db)) -> DefaultLeadService:
    """
    Dependency to get the lead service instance with properly initialized repository.
    """
    try:
        lead_repository = PostgresLeadRepository(db)
        return DefaultLeadService(lead_repository)
    except Exception as e:
        logger.error(f"Error creating lead service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initializing lead service"
        )

async def get_campaign_service(db: AsyncSession = Depends(get_db)) -> DefaultCampaignService:
    """
    Dependency to get the campaign service instance with properly initialized repository.
    """
    try:
        campaign_service = await create_campaign_service_async(session=db)
        return campaign_service
    except Exception as e:
        logger.error(f"Error creating campaign service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initializing campaign service"
        )

