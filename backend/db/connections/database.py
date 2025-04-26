from ..config import settings
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import exc, text  # Added the text import
from urllib.parse import urlparse, parse_qs
import asyncio
import logging

logger = logging.getLogger(__name__)

# Parse the database URL to handle SSL configuration properly
def get_engine_args():
    url = settings.DATABASE_URL
    connect_args = {}
    
    # Handle SSL specifically for Neon
    if 'neon.tech' in url:
        # For asyncpg and Neon, remove sslmode from URL and set SSL in connect_args
        parsed_url = urlparse(url)
        query_dict = parse_qs(parsed_url.query)
        
        # Remove SSL parameters from the URL
        clean_url = url
        if 'sslmode' in parsed_url.query:
            for param in ['sslmode=require', 'sslmode=verify-full']:
                if param in clean_url:
                    clean_url = clean_url.replace(f"&{param}", "").replace(f"?{param}", "")
        
        # Set proper SSL configuration for asyncpg
        connect_args['ssl'] = True
        
        # Add connection timeout and command_timeout settings
        connect_args['command_timeout'] = 30  # 30 second timeout for commands
        connect_args['timeout'] = 10  # 10 second connection timeout
        
        return clean_url, connect_args
    
    return url, connect_args

# Get cleaned URL and connection arguments
db_url, connect_args = get_engine_args()

# Create the async engine with proper connection arguments
engine = create_async_engine(
    db_url, 
    echo=False,  # Set to False in production
    connect_args=connect_args,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=10,        # Maximum number of persistent connections
    max_overflow=15,     # Maximum number of connections above pool_size
    pool_recycle=1800,   # Recycle connections after 30 minutes
    pool_timeout=30      # Pool timeout in seconds
)

# Add a safer SessionLocal function
def get_safe_session():
    """
    Get a database session with safer defaults for worker tasks.
    This increases timeouts and retry capabilities.
    """
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        future=True
        # Remove these parameters - they belong only to the engine config:
        # pool_pre_ping=True,
        # pool_recycle=1800,
        # pool_timeout=30
    )()

# Override the SessionLocal with our safer version
SessionLocal = get_safe_session

# Maximum retries for database operations
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds

# This function should be used as a FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session as a dependency.
    For use with FastAPI's dependency injection system.
    
    Includes retry logic for transient connection issues.
    """
    session = SessionLocal()
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            # Test the connection with a ping before returning it
            await session.execute(text("SELECT 1"))  # Added text() wrapper
            
            # If we reach here, connection is good
            try:
                yield session
                await session.commit()
                break
            except Exception as e:
                await session.rollback()
                logger.error(f"Database error, rolling back transaction: {str(e)}")
                raise
            finally:
                await session.close()
                
        except (exc.OperationalError, exc.InterfaceError) as e:
            await session.close()
            retry_count += 1
            
            if retry_count >= MAX_RETRIES:
                logger.error(f"Failed to connect to database after {MAX_RETRIES} attempts: {str(e)}")
                raise
                
            logger.warning(f"Database connection error (attempt {retry_count}/{MAX_RETRIES}): {str(e)}")
            await asyncio.sleep(RETRY_DELAY * retry_count)  # Exponential backoff
            session = SessionLocal()  # Create a new session for retry

async def check_db_connection() -> bool:
    """
    Check if the database connection is working.
    Useful for health checks.
    """
    try:
        session = SessionLocal()
        try:
            await session.execute(text("SELECT 1"))  # Added text() wrapper
            return True
        finally:
            await session.close()
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

async def get_db_session() -> AsyncSession:
    """
    Get a database session directly.
    This returns the session object directly rather than yielding it.
    
    Returns:
        AsyncSession: A SQLAlchemy async session
    """
    session = SessionLocal()
    try:
        # Test the connection with a ping
        await session.execute(text("SELECT 1"))
        return session
    except (exc.OperationalError, exc.InterfaceError) as e:
        await session.close()
        logger.error(f"Failed to connect to database: {str(e)}")
        raise