from sqlalchemy.ext.asyncio import AsyncSession

from core.connection_to_db import engine
from models.models import Note
from .base_service import BaseService


class NoteService(BaseService):
    async def create_new_note(
            self, title, text, is_pinned, user_id, category_id, tg_url):
        async with AsyncSession(engine) as session:
            try:
                new_note = Note(
                    title=title,
                    text=text,
                    is_pinned=is_pinned,
                    user_id=user_id,
                    category_id=category_id,
                    link_to_forwd_msg=tg_url)
                session.add(new_note)
                await session.commit()
                await session.refresh(new_note)
                await self.send_message_for_admin(
                    'Пользователь c id'
                    f'{user_id} создал новую заметку.')
            except Exception as e:
                await self.send_message_for_admin(
                    f'Возникла ошибка при создании новой заметки'
                    f'пользователем с user_id {user_id}'
                    f'{e}')
                await session.rollback()
        await engine.dispose()

    async def edit_note(
            self, note_obj, title, text, is_pinned,
            category_id, tg_url):
        async with AsyncSession(engine) as session:
            try:
                note_obj.title = title
                note_obj.text = text
                note_obj.is_pinned = is_pinned
                note_obj.category_id = category_id
                note_obj.link_to_forwd_msg = tg_url
                await session.commit()
                await session.refresh(note_obj)
            except Exception as e:
                print(f'Ошибка при создании заметки: {e}')
                await session.rollback()
                raise
        await engine.dispose()
