from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from src.app.bot.create_bot import bot
from bot.keyboards.user_kbs import (
    main_user_keyboard, user_inline_keyboard_for_pin_notes,
    admin_inline_keyboard_for_management_users)
from core.connection_to_db import AsyncSessionLocal
from src.app.utils import (
    check_user_telegram_id_in_db, get_user_id_and_token_by_telegram_id,
    get_user_pin_notes, get_num_note_pgs, get_category_title_by_id,
    shorting_text, get_user_note_by_id_without_user_id,
    check_is_admin_by_user_id, get_users_with_notes,
    get_user_obj_by_user_id)
from src.app.token_encryption import encryption
from src.app.crud import note_crud, user_crud, category_crud
from src.app.bot_utils import send_message_for_admin


user_router_bot = Router()


@user_router_bot.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    async with AsyncSessionLocal() as session:
        if not await check_user_telegram_id_in_db(
                message.from_user.id, session):
            user_obj_in_data = {
                'telegram_id': message.from_user.id,
                'is_active': True,
                'is_admin': False}
            new_user = await user_crud.create(user_obj_in_data, session)
            category_obj_in_data = {
                'title': 'Без категории',
                'user_id': new_user.id}
            await category_crud.create(category_obj_in_data, session)
            await send_message_for_admin(
                f'Создан новый пользователь '
                f'с telegram_id {new_user.telegram_id}')

        user_id, user_token = await get_user_id_and_token_by_telegram_id(
            message.from_user.id, session)

        is_admin = await check_is_admin_by_user_id(user_id, session)
        # is_admin = False

    user_token = encryption(user_token)
    await message.answer(
        'Выберите действие:',
        reply_markup=main_user_keyboard(user_id, user_token, is_admin))


@user_router_bot.message(
    lambda message: message.text in ['Показать закрепленные заметки'])
async def show_pinned_notes(message: types.Message):
    async with AsyncSessionLocal() as session:
        user_id, user_token = await get_user_id_and_token_by_telegram_id(
            message.from_user.id, session)
    user_token = encryption(user_token)
    user_pin_notes = await get_user_pin_notes(user_id)
    current_message_id = message.message_id
    for obj in user_pin_notes:
        current_message_id += 1
        async with AsyncSessionLocal() as session:
            try:
                num_note_pgs = await get_num_note_pgs(obj.category_id, session)
                category_title = await get_category_title_by_id(
                    user_id, obj.category_id, session)
                obj.text = shorting_text(obj.text, 30)
                text = (
                    f'<b>Категория:</b> {category_title} \n'
                    f'<b>Название:</b> {obj.title} \n'
                    f'<b>Текст:</b> {obj.text}')
                await message.answer(
                    text=text, parse_mode='HTML',
                    reply_markup=user_inline_keyboard_for_pin_notes(
                        obj.id, obj.category_id, num_note_pgs,
                        user_id, user_token, current_message_id))
            except Exception:
                pass
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(user_pin_notes)
    if not user_pin_notes:
        await message.answer(
            text='У Вас нет закрепленных заметок', parse_mode='HTML')


@user_router_bot.callback_query(F.data.startswith('delete_msg'))
async def delete_msg(call: CallbackQuery):
    msg_id = int(call.data.replace('delete_msg_', ''))
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=msg_id)


@user_router_bot.callback_query(F.data.startswith('unpin_note_'))
async def unpin_note(call: CallbackQuery):
    note_id = int(call.data.split('_')[-2])
    current_message = call.data.split('_')[-1]
    async with AsyncSessionLocal() as session:
        note_obj = await get_user_note_by_id_without_user_id(note_id, session)
        await note_crud.update(note_obj, {'is_pinned': False}, session)
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=int(current_message))


@user_router_bot.message(
    lambda message: message.text in ['Показать пользователей'])
async def manage_users(message: types.Message):
    async with AsyncSessionLocal() as session:
        user_id, user_token = await get_user_id_and_token_by_telegram_id(
            message.from_user.id, session)
        if not await check_is_admin_by_user_id(user_id, session):
            await message.answer(
                text='Такой команды нет', parse_mode='HTML')
        users = await get_users_with_notes(session)
        for user in users:
            setattr(user, 'status', 'Разрешен')
            if not user.is_active:
                user.status = 'Заблокирован'
            text = (
                f'<b>User id:</b> {user.id}\n'
                f'<b>Кол-во заметок:</b> {len(user.notes)}\n'
                f'<b>Telegram_id:</b> {user.telegram_id} \n'
                f'<b>Доступ к боту:</b> {user.status}')
            await message.answer(
                text=text, parse_mode='HTML',
                reply_markup=admin_inline_keyboard_for_management_users(
                    user.id, user.is_active))


@user_router_bot.callback_query(F.data.startswith('deactivate_user_'))
async def deactivate_user(call: CallbackQuery):
    user_id = int(call.data.split('_')[-1])
    async with AsyncSessionLocal() as session:
        user_obj = await get_user_obj_by_user_id(user_id, session)
        await user_crud.update(user_obj, {'is_active': False}, session)
    await call.message.edit_text(
        f'❌ Вы запретили доступ к боту пользователю с user_id {user_obj.id} и '
        f'telegram_id {user_obj.telegram_id}')
    await call.answer()


@user_router_bot.callback_query(F.data.startswith('activate_user_'))
async def activate_user(call: CallbackQuery):
    user_id = int(call.data.split('_')[-1])
    async with AsyncSessionLocal() as session:
        user_obj = await get_user_obj_by_user_id(user_id, session)
        await user_crud.update(user_obj, {'is_active': True}, session)
    await call.message.edit_text(
        f'✅ Вы разблокировали доступ к боту пользователю с user_id '
        f'{user_obj.id} и telegram_id {user_obj.telegram_id}')


@user_router_bot.callback_query(F.data.startswith('delete_user_'))
async def delete_user(call: CallbackQuery):
    user_id = int(call.data.split('_')[-1])
    async with AsyncSessionLocal() as session:
        user_obj = await get_user_obj_by_user_id(user_id, session)
        await user_crud.delete(user_obj, session)
