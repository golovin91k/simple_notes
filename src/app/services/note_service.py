import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import BASE_DIR
from core.connection_to_db import engine
from models.models import Note
from .base_service import BaseService


class NoteService(BaseService):
    async def create_new_note(
            self, title, text, is_pinned, user_id, category_id):
        # async with AsyncSession(engine) as session:
        #     try:
        #         new_note = Note(
        #             title=title,
        #             text=text,
        #             is_pinned=is_pinned,
        #             user_id=user_id,
        #             category_id=category_id)
        #         session.add(new_note)
        #         await session.commit()
        #         await session.refresh(new_note)
        #         await self.send_message_for_admin(
        #             'Пользователь c id'
        #             f'{user_id} создал новую заметку.')
        #         return new_note
        #     except Exception as e:
        #         await self.send_message_for_admin(
        #             f'Возникла ошибка при создании новой заметки '
        #             f'пользователем с user_id {user_id} '
        #             f'{e}')
        #         await session.rollback()
        #     finally:
        #     await engine.dispose()
        # try:
        #     return new_note
        # except Exception:
        #     pass
        try:
            async with AsyncSession(engine) as session:
                
                new_note = Note(
                    title=title,
                    text=text,
                    is_pinned=is_pinned,
                    user_id=user_id,
                    category_id=category_id)
                session.add(new_note)
                await session.commit()
                await session.refresh(new_note)
                await self.send_message_for_admin(
                    'Пользователь c id'
                    f'{user_id} создал новую заметку.')
                directory = os.path.join(BASE_DIR, 'src/statics')

                await self.send_message_for_admin(f'{directory}')
                return new_note
        except Exception as e:
            await self.send_message_for_admin(
                f'Возникла ошибка при создании новой заметки '
                f'пользователем с user_id {user_id} '
                f'{e}')
            await session.rollback()
        finally:
            await engine.dispose()


    async def edit_note(
            self, note_id, title, text, is_pinned,
            category_id):
        async with AsyncSession(engine) as session:
            try:
                note_obj = await session.execute(select(Note).where(
                    Note.id == note_id))  # , Note.user_id == user_id))
                note_obj = note_obj.scalars().first()
                note_obj.title = title
                note_obj.text = text
                note_obj.is_pinned = is_pinned
                note_obj.category_id = category_id
                await session.commit()
                await session.refresh(note_obj)
            except Exception as e:
                print(f'Ошибка при редактировании заметки: {e}')
                await session.rollback()
        await engine.dispose()
        try:
            return note_obj
        except Exception:
            pass

    async def delete_note(self, note_id):
        async with AsyncSession(engine) as session:
            try:
                note_obj = await session.execute(select(Note).where(
                    Note.id == note_id))  # , Note.user_id == user_id))
                note_obj = note_obj.scalars().first()
                await session.delete(note_obj)
                await session.commit()
            except Exception as e:
                print(f'Ошибка при удалении заметки: {e}')
                await session.rollback()
        await engine.dispose()
