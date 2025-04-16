
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from src.app.models.note import Note


class CRUDNote(CRUDBase):
    async def delete(self, db_obj, session: AsyncSession):
        await session.delete(db_obj)
        await session.commit()
        return db_obj


note_crud = CRUDNote(Note)
