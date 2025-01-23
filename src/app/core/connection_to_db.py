from functools import wraps

from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine)
from sqlalchemy.orm import sessionmaker

from .config import settings


engine = create_async_engine(settings.get_db_url)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


def create_async_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSession(engine) as session:
            result = await func(*args, session=session, **kwargs)
        await engine.dispose()
        return result
    return wrapper
