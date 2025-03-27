from ..config import settings
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, parse_qs

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
        
        return clean_url, connect_args
    
    return url, connect_args

# Get cleaned URL and connection arguments
db_url, connect_args = get_engine_args()

# Create the async engine with proper connection arguments
engine = create_async_engine(
    db_url, 
    echo=True,
    connect_args=connect_args
)

# Configure the async session maker
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()