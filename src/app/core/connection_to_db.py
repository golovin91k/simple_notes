from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine)
from sqlalchemy.orm import sessionmaker

from .config import settings


# def create_engine():
#     return create_async_engine(settings.get_db_url)


# async_session = sessionmaker(
#     bind=create_engine(),
#     class_=AsyncSession,
#     expire_on_commit=False)


engine = create_async_engine(settings.get_db_url)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


async def try_1(func):
    async def wrapper():
        async with AsyncSession(engine) as session:
            func()
        await engine.dispose()
    return wrapper
# async def get_async_session():
#     # Через асинхронный контекстный менеджер и sessionmaker
#     # открывается сессия.
#     async with AsyncSessionLocal() as async_session:
#         # Генератор с сессией передается в вызывающую функцию.
#         yield async_session
#         # Когда HTTP-запрос отработает - выполнение кода вернётся сюда,
#         # и при выходе из контекстного менеджера сессия будет закрыта.

