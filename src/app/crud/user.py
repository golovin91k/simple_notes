import random
import secrets

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from src.app.models.user import User


class CRUDUser(CRUDBase):
    async def create(self, obj_in_data, session: AsyncSession):
        obj_in_data['token'] = await self.generate_token(session)
        new_user = User(**obj_in_data)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def check_token(self, token_for_checking, session):
        tokens_from_db = await session.execute(
            select(User.token).where(User.token == token_for_checking))
        tokens_from_db = tokens_from_db.scalars().first()
        if tokens_from_db:
            return True
        return False

    async def generate_token(self, session):
        random_number = random.randint(15, 30)
        token = secrets.token_hex(random_number)
        while await self.check_token(token, session):
            random_number = random.randint(15, 30)
            token = secrets.token_hex(random_number)
        return token

    async def delete(self, db_obj, session: AsyncSession):
        await session.delete(db_obj)
        await session.commit()
        return db_obj


user_crud = CRUDUser(User)
