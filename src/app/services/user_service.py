import random
import secrets

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.connection_to_db import engine
from models.models import User, Category
from bot.create_bot import bot


class UserService:
    async def create_new_user(self, telegram_id, is_admin=False):
        async with AsyncSession(engine) as session:
            new_user = User(
                telegram_id=telegram_id,
                token=await self.generate_token(),
                is_admin=is_admin)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
        await engine.dispose()
        await self.create_category_without_a_title(new_user.id)
        await self.send_message_for_admin('Создан новый пользователь.')

    async def check_token(self, token_for_checking):
        async with AsyncSession(engine) as session:
            tokens_from_db = await session.execute(
                select(User.token).where(User.token == token_for_checking))
            tokens_from_db = tokens_from_db.scalars().first()
        await engine.dispose()
        if tokens_from_db:
            return True
        return False

    async def generate_token(self):
        random_number = random.randint(15, 30)
        token = secrets.token_hex(random_number)
        while await self.check_token(token):
            random_number = random.randint(15, 30)
            token = secrets.token_hex(random_number)
        return token

    async def create_category_without_a_title(self, user_id):
        async with AsyncSession(engine) as session:
            cat_without_title = Category(
                title='Без категории',
                user_id=user_id)
            session.add(cat_without_title)
            await session.commit()
            await session.refresh(cat_without_title)
        await engine.dispose()

    async def send_message_for_admin(self, message):
        try:
            await bot.send_message(
                settings.ADMIN_TELEGRAM_ID, message)
        except Exception:
            pass
