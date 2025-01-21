# from sqlalchemy.future import select
# import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from core.connection_to_db import engine
from models.models import Note


class NoteService():
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
                print('sozdana novaya zametka')
            except Exception as e:
                print(f'Ошибка при создании заметки: {e}')
                await session.rollback()
                raise
        await engine.dispose()
