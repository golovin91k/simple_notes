from sqlalchemy.ext.asyncio import AsyncSession

from core.connection_to_db import engine
from models.models import Category


class CategoryService():
    async def create_new_category(
            self, title, user_id):
        async with AsyncSession(engine) as session:
            try:
                new_category = Category(
                    title=title,
                    user_id=user_id)
                session.add(new_category)
                await session.commit()
                await session.refresh(new_category)
                print('sozdana novaya categoriya')
            except Exception as e:
                print(f'Ошибка при создании категории: {e}')
                await session.rollback()
                raise
        await engine.dispose()
