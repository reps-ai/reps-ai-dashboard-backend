
from ..config import settings
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Create the async engine (ensure your DATABASE_URL is in the correct async format)
engine = create_async_engine(settings.database_url_with_ssl, echo=True)

# Configure the async session maker
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session