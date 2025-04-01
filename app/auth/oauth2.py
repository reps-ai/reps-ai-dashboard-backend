"""
OAuth2 authentication with JWT tokens for the Reps AI Dashboard.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv

from ..dependencies import User, Branch
from backend.db.connections.database import get_db
from backend.db.models.user import User as DBUser
from backend.db.models.gym.branch import Branch as DBBranch

# Load environment variables
load_dotenv()

# Create OAuth2 scheme pointing to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Token settings directly from environment variables
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-replace-in-production")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class TokenData:
    """Class to store the data extracted from a token."""
    def __init__(self, user_id: Optional[int] = None, branch_id: Optional[uuid.UUID] = None, gym_id: Optional[uuid.UUID] = None):
        self.user_id = user_id
        self.branch_id = branch_id
        self.gym_id = gym_id


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a new JWT token with the provided data.
    
    Args:
        data: Dictionary of data to encode in the token
        
    Returns:
        JWT token string
    """
    # Make a copy of the data to avoid modifying the original
    to_encode = data.copy()
    
    # Add expiration time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create the JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def verify_access_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        credentials_exception: Exception to raise if token is invalid
        
    Returns:
        TokenData containing the decoded data
        
    Raises:
        HTTPException: If token verification fails
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user ID, branch ID and gym ID
        user_id = payload.get("user_id")
        branch_id = payload.get("branch_id")
        gym_id = payload.get("gym_id")
        
        # Convert IDs to proper types
        if user_id:
            try:
                user_id = int(user_id) if user_id.isdigit() else uuid.UUID(user_id)
            except (ValueError, AttributeError):
                raise credentials_exception
                
        if branch_id:
            branch_id = uuid.UUID(branch_id)  # Converting branch_id back to UUID
        if gym_id:
            gym_id = uuid.UUID(gym_id)
        
        if user_id is None:
            raise credentials_exception
        
        # Return token data
        token_data = TokenData(user_id=user_id, branch_id=branch_id, gym_id=gym_id)
        return token_data
        
    except JWTError:
        raise credentials_exception


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)) -> User:
    """
    Get current user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        session: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify the token
    token_data = await verify_access_token(token, credentials_exception)
    
    # Get the user from database
    query = select(DBUser).where(DBUser.id == token_data.user_id)
    result = await session.execute(query)
    db_user = result.scalar_one_or_none()
    
    if db_user is None:
        raise credentials_exception
    
    # Determine admin status based on role
    is_admin = db_user.role in ["admin", "manager"]
    
    # Create a user object with proper field assignments
    user = User(
        id=db_user.id,
        email=db_user.email,
        first_name=db_user.first_name,  
        last_name=db_user.last_name,    
        role=db_user.role,              
        is_admin=is_admin,              # Derived from role
        gym_id=db_user.gym_id
    )
    
    # Add branch_id from db_user, not from user (fixes branch_id assignment bug)
    user.branch_id = db_user.branch_id
    
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user and verify they have admin privileges.
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        The current user if they are an admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return current_user


async def get_current_branch(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_db)
) -> Branch:
    """
    Get the branch associated with the current user.
    
    Args:
        token: JWT token
        session: Database session
        
    Returns:
        Branch object
        
    Raises:
        HTTPException: If branch not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify the token
    token_data = await verify_access_token(token, credentials_exception)
    
    # Get the branch from database using branch_id from token
    query = select(DBBranch).where(DBBranch.id == token_data.branch_id)
    result = await session.execute(query)
    branch_data = result.scalar_one_or_none()
    
    if branch_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch not found"
        )
    
    # Create a branch object
    branch = Branch(
        id=branch_data.id,
        gym_id=branch_data.gym_id,
        name=branch_data.name
    )
    
    return branch
