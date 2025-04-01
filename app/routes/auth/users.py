"""
User management routes for authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
import uuid

from app.schemas.auth import UserCreate
from app.dependencies import get_admin_user, User
from backend.db.connections.database import get_db
from backend.db.models.user import User as DBUser
from backend.db.models.gym.branch import Branch as DBBranch
from backend.utils.logging.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_admin_user),  # Only admins can create users
    session: AsyncSession = Depends(get_db)
):
    """
    Create a new user account.
    
    Args:
        user_data: User data for creation
        current_user: Currently authenticated admin user
        session: Database session
    
    Returns:
        New user data (without password)
    """
    # Check if email is already taken
    query = select(DBUser).where(DBUser.email == user_data.email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if (existing_user):
        logger.warning(f"User creation failed: Email {user_data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify that the branch exists
    try:
        # Explicitly convert branch_id to UUID to ensure correct type
        branch_uuid = uuid.UUID(str(user_data.branch_id))
        branch_query = select(DBBranch).where(DBBranch.id == branch_uuid)
        branch_result = await session.execute(branch_query)
        branch = branch_result.scalar_one_or_none()
        
        if not branch:
            logger.warning(f"User creation failed: Branch {branch_uuid} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch with ID {branch_uuid} not found"
            )
    except ValueError:
        logger.warning(f"User creation failed: Invalid branch ID format {user_data.branch_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid branch ID format: {user_data.branch_id}"
        )
    
    # Hash the password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Generate username if not provided (use email username part or first_name.last_name)
    username = user_data.username
    if not username:
        email_username = user_data.email.split('@')[0]
        if len(email_username) > 3 and not await is_username_taken(session, email_username):
            username = email_username
        else:
            base_username = f"{user_data.first_name.lower()}.{user_data.last_name.lower()}"
            username = base_username
            counter = 1
            # Check if username exists and append counter if it does
            while await is_username_taken(session, username):
                username = f"{base_username}_{counter}"
                counter += 1
    
    # Instead of creating the user with an explicit ID, let the model handle it
    new_user = DBUser(
        # Don't set ID at all - let the database generate it with its default
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        branch_id=branch_uuid,
        gym_id=branch.gym_id,
        role=user_data.role,
        username=username  # Add the username
    )
    
    # Save to database
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    logger.info(f"User created successfully: {new_user.email} (ID: {new_user.id})")
    
    # Update return format to include first and last name separately
    # Also map role to is_admin for consistency with existing API
    is_admin = new_user.role in ["admin", "manager"]
    
    # Return user data without password
    return {
        "id": new_user.id,
        "email": new_user.email,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "branch_id": str(new_user.branch_id),
        "gym_id": str(new_user.gym_id),
        "role": new_user.role,
        "is_admin": is_admin,
        "message": "User created successfully"
    }

# Helper function to check if a username is already taken
async def is_username_taken(session: AsyncSession, username: str) -> bool:
    """Check if a username is already taken."""
    query = select(DBUser).where(DBUser.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None
