from sqlalchemy.ext.asyncio import AsyncSession

from core.connection_to_db import engine
from models.models import Category
from .base_service import BaseService


class CategoryService(BaseService):
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
            except Exception as e:
                await self.send_message_for_admin(
                    f'Возникла ошибка при создании новой'
                    f'категории с названием {title}'
                    f'пользователем с user_id {user_id}'
                    f'{e}')
                await session.rollback()
        await engine.dispose()
