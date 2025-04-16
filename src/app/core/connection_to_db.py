from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine)
from sqlalchemy.orm import sessionmaker

from .config import settings


engine = create_async_engine(settings.get_db_url)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
