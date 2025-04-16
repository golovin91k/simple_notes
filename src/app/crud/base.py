from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.bot_utils import send_message_for_admin
from src.app.models.note import Note


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def create(
            self,
            obj_in_data,
            session: AsyncSession):
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        if self.model == Note:
            await send_message_for_admin(
                'Пользователь c id '
                f'{db_obj.user_id} создал новую заметку.')
        return db_obj

    async def update(
            self, db_obj, update_data, session: AsyncSession):
        obj_data = jsonable_encoder(db_obj)
        for field in update_data:
            if field in obj_data:
                setattr(db_obj, field, update_data[field])
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
