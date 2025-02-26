from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.connection_to_db import create_async_session, engine
from models.models import User, Note, Category
from services.user_service import UserService
from bot.create_bot import bot


@create_async_session
async def check_user_telegram_id_in_db(telegram_id, session=None):
    db_obj = await session.execute(select(User).where(
        User.telegram_id == telegram_id))
    db_obj = db_obj.scalars().first()
    if db_obj:
        return True
    return False


async def get_user_id_and_token_by_telegram_id(telegram_id):
    async with AsyncSession(engine) as session:
        db_obj = await session.execute(select(User).where(
            User.telegram_id == telegram_id))
        db_obj = db_obj.scalars().first()
    await engine.dispose()
    if db_obj:
        return db_obj.id, db_obj.token
    return None


@create_async_session
async def check_user_id_and_user_token(user_id, user_token, session=None):
    db_obj = await session.execute(select(User).where(
        User.id == user_id))
    db_obj = db_obj.scalars().first()
    if db_obj and db_obj.token == user_token:
        return True
    return False


async def create_user_admin():
    service = UserService()
    await service.create_new_user(
            settings.ADMIN_TELEGRAM_ID, is_admin=True)


async def get_user_notes(user_id):
    async with AsyncSession(engine) as session:
        db_obj = await session.execute(select(Note).where(
            Note.user_id == user_id))
        db_obj = db_obj.scalars().all()
    await engine.dispose()
    return_list = []
    for obj in db_obj:
        return_list.append(obj.text)
    return return_list


async def get_user_categories(user_id):
    async with AsyncSession(engine) as session:
        db_obj = await session.execute(select(Category).where(
            Category.user_id == user_id))
        db_obj = db_obj.scalars().all()
    await engine.dispose()
    return_list = []
    for obj in db_obj:
        return_list.append(obj.title)
    return return_list


async def get_category_id_by_title(user_id, title):
    async with AsyncSession(engine) as session:
        db_obj = await session.execute(select(Category).where(
            Category.title == title, Category.user_id == user_id))
        db_obj = db_obj.scalars().first()
    await engine.dispose()
    return db_obj.id


async def create_test_data():
    async with AsyncSession(engine) as session:
        db_obj = await session.execute(select(User).where(
            User.id == 6))
        db_obj = db_obj.scalars().all()
        for obj in db_obj:
            await session.delete(obj)
        await session.commit()


async def send_message_for_admin(message):
    try:
        await bot.send_message(
            settings.ADMIN_TELEGRAM_ID, message)
    except Exception:
        pass


async def get_number_user_pin_notes(user_id):
    async with AsyncSession(engine) as session:
        db_objs = await session.execute(select(Note).where(
            Note.user_id == user_id, Note.is_pinned == True))
        db_objs = db_objs.scalars().all()
    await engine.dispose()
    return len(db_objs)


async def get_user_pin_notes(user_id):
    async with AsyncSession(engine) as session:
        db_objs = await session.execute(select(Note).where(
            Note.user_id == user_id, Note.is_pinned == True))
        db_objs = db_objs.scalars().all()
    await engine.dispose()
    return db_objs


async def get_user_categories_and_notes(user_id):
    async with AsyncSession(engine) as session:
        stmt = select(Category).where(Category.user_id == user_id).options(
            joinedload(Category.notes))
        result = await session.execute(stmt)
        categories = result.unique().scalars().all()
        for category in categories:
            latest_note = max(
                category.notes, key=lambda note: note.updated_at, default=None)
            setattr(category, 'latest_note', latest_note)

            num_note_pgs = (len(category.notes) // 6)
            if ((len(category.notes) % 6) != 0) or (len(category.notes) == 0):
                num_note_pgs = (len(category.notes) // 6) + 1
            setattr(category, 'num_note_pgs', num_note_pgs)

    await engine.dispose()
    return categories


async def get_user_notes_by_category_id(
        category_id, skip, limit):
    async with AsyncSession(engine) as session:
        db_objs = await session.execute(select(Note).where(
            Note.category_id == category_id).order_by(
                Note.updated_at).offset(skip).limit(limit))
        db_objs = db_objs.scalars().all()
    await engine.dispose()
    return db_objs


async def get_count_notes_by_category_id(category_id):
    async with AsyncSession(engine) as session:
        db_objs = await session.execute(select(Note).where(
            Note.category_id == category_id))
        db_objs = db_objs.scalars().all()
    await engine.dispose()
    return len(db_objs)


async def get_user_note_by_id(note_id):
    async with AsyncSession(engine) as session:
        db_obj = await session.execute(select(Note).where(
            Note.id == note_id))
        db_obj = db_obj.scalars().first()
    await engine.dispose()
    return db_obj


@create_async_session
async def check_user_id_and_category_id(user_id, category_id, session=None):
    db_obj = await session.execute(select(Category).where(
        Category.id == category_id, Category.user_id == user_id))
    db_obj = db_obj.scalars().first()
    if db_obj:
        return True
    return False
