from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.create_bot import bot
from core.config import settings
from core.connection_to_db import engine
from models import User, Note, Category
from src.app.constants import (
    NUMBER_OF_NOTES_PER_PAGE, NUMBER_OF_WORDS_TO_REDUCE)
from src.app.crud import category_crud, user_crud


async def check_user_telegram_id_in_db(
        telegram_id: int, session: AsyncSession):
    db_obj = await session.execute(select(User).where(
        User.telegram_id == telegram_id))
    db_obj = db_obj.scalars().first()
    return bool(db_obj)


async def get_user_id_and_token_by_telegram_id(telegram_id, session):
    db_obj = await session.execute(select(User).where(
        User.telegram_id == telegram_id))
    db_obj = db_obj.scalars().first()
    if db_obj:
        return db_obj.id, db_obj.token
    return None


async def check_user_id_and_user_token(
        user_id: int, user_token: str, session: AsyncSession):
    db_obj = await session.execute(select(User).where(
        User.id == user_id))
    db_obj = db_obj.scalars().first()
    return bool(db_obj and db_obj.token == user_token)


async def create_user_admin():
    async with AsyncSession(engine) as session:
        user_admin_obj_in_data = {
            'telegram_id': settings.ADMIN_TELEGRAM_ID,
            'is_active': True,
            'is_admin': True}
        admin = await user_crud.create(user_admin_obj_in_data, session)
        category_obj_in_data = {
            'title': 'Без категории',
            'user_id': admin.id}
        await category_crud.create(category_obj_in_data, session)


async def get_user_categories_title(user_id: int, session: AsyncSession):
    db_objs = await session.execute(select(Category.title).where(
        Category.user_id == user_id))
    db_objs = db_objs.scalars().all()
    return db_objs


async def get_category_id_by_title(
        user_id: int, title: str, session: AsyncSession):
    db_obj = await session.execute(select(Category.id).where(
        Category.title == title, Category.user_id == user_id))
    db_obj = db_obj.scalars().first()
    return db_obj


async def get_category_obj_by_id(id: int, session: AsyncSession):
    db_obj = await session.execute(select(Category).where(
        Category.id == id))
    db_obj = db_obj.scalars().first()
    return db_obj


async def get_category_title_by_id(
        user_id: int, category_id: int, session: AsyncSession):
    db_obj = await session.execute(select(Category).where(
        Category.id == category_id, Category.user_id == user_id))
    db_obj = db_obj.scalars().first()
    return db_obj.title


async def get_category_id_by_note_id(
        user_id: int, note_id: int, session: AsyncSession):
    db_obj = await session.execute(select(
        Note.category_id).where(Note.id == note_id))
    db_obj = db_obj.scalars().first()
    return db_obj


async def send_message_for_admin(message):
    try:
        await bot.send_message(
            settings.ADMIN_TELEGRAM_ID, message)
    except Exception:
        pass


async def send_message_for_all_users(message):
    async with AsyncSession(engine) as session:
        db_objs = await session.execute(select(User.telegram_id))
        db_objs = db_objs.scalars().all()
    for obj in db_objs:
        await bot.send_message(obj, message)
    await engine.dispose()


async def get_number_user_pin_notes(user_id: int, session: AsyncSession):
    db_objs = await session.execute(select(Note).where(
        Note.user_id == user_id, Note.is_pinned == True))
    db_objs = db_objs.scalars().all()
    return len(db_objs)


async def get_user_pin_notes(user_id):
    async with AsyncSession(engine) as session:
        db_objs = await session.execute(select(Note).where(
            Note.user_id == user_id, Note.is_pinned == True))
        db_objs = db_objs.scalars().all()
    await engine.dispose()
    return db_objs


async def get_user_categories_and_notes(user_id: int, session: AsyncSession):
    stmt = select(Category).where(Category.user_id == user_id).options(
        joinedload(Category.notes))
    result = await session.execute(stmt)
    categories = result.unique().scalars().all()

    for category in categories:
        latest_note = max(
            category.notes, key=lambda note: note.updated_at, default=None)
        if latest_note:
            latest_note.updated_at = latest_note.updated_at.strftime(
                '%d.%m.%Y %H:%M')
            latest_note.text = shorting_text(
                latest_note.text, NUMBER_OF_WORDS_TO_REDUCE)
        setattr(category, 'latest_note', latest_note)
        num_note_pgs = (len(category.notes) // NUMBER_OF_NOTES_PER_PAGE)
        if (((len(category.notes) % NUMBER_OF_NOTES_PER_PAGE) != 0) or
                (len(category.notes) == 0)):
            num_note_pgs = (len(category.notes) //
                            NUMBER_OF_NOTES_PER_PAGE) + 1
        setattr(category, 'num_note_pgs', num_note_pgs)
    return categories


async def get_user_notes_by_category_id(
        category_id: int, skip: int, limit: int, session: AsyncSession):
    db_objs = await session.execute(select(Note).where(
        Note.category_id == category_id).order_by(
            desc(Note.updated_at)).offset(skip).limit(limit))
    db_objs = db_objs.scalars().all()
    for obj in db_objs:
        setattr(obj, 'shorting_text', shorting_text(
            obj.text, NUMBER_OF_WORDS_TO_REDUCE))
        setattr(
            obj, 'updated_at_str', obj.updated_at.strftime("%d.%m.%Y %H:%M"))
    return db_objs


async def get_count_notes_by_category_id(
        category_id: int, session: AsyncSession):
    db_objs = await session.execute(select(Note).where(
        Note.category_id == category_id))
    db_objs = db_objs.scalars().all()
    return len(db_objs)


async def get_num_note_pgs(category_id: int, session: AsyncSession):
    count_notes = await get_count_notes_by_category_id(category_id, session)
    num_note_pgs = 1
    if (count_notes // NUMBER_OF_NOTES_PER_PAGE != 0 and
            count_notes % NUMBER_OF_NOTES_PER_PAGE != 0):
        num_note_pgs = (count_notes // NUMBER_OF_NOTES_PER_PAGE) + 1
    elif (count_notes // NUMBER_OF_NOTES_PER_PAGE != 0 and
          count_notes % NUMBER_OF_NOTES_PER_PAGE == 0):
        num_note_pgs = (count_notes // NUMBER_OF_NOTES_PER_PAGE)
    return num_note_pgs


async def get_user_note_by_id(
        user_id: int, note_id: int, session: AsyncSession):
    db_obj = await session.execute(select(Note).where(
        Note.id == note_id, Note.user_id == user_id))
    db_obj = db_obj.scalars().first()
    return db_obj


async def get_user_note_by_id_without_user_id(
        note_id: int, session: AsyncSession):
    db_obj = await session.execute(select(Note).where(
        Note.id == note_id))
    db_obj = db_obj.scalars().first()
    return db_obj


def shorting_text(text, max_len):
    text = text.split()
    result_text = []
    while text and len(result_text) < max_len:
        if len(text[0]) <= 10:
            result_text.append(text[0])
        else:
            result_text.append('...')
        text.pop(0)
    result_text = ' '.join(result_text)
    return result_text


async def check_is_admin_by_user_id(
        user_id, session: AsyncSession):
    db_obj = await session.execute(select(User.is_admin).where(
        User.id == user_id))
    db_obj = db_obj.scalars().first()
    return db_obj


async def get_users_with_notes(session: AsyncSession):
    stmt = select(User).options(
        joinedload(User.notes))
    result = await session.execute(stmt)
    users = result.unique().scalars().all()
    return users


async def get_user_obj_by_user_id(user_id, session: AsyncSession):
    db_obj = await session.execute(select(User).where(
        User.id == user_id))
    db_obj = db_obj.scalars().first()
    return db_obj
