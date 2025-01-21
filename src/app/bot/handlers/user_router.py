from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

# from bot.create_bot import bot
from bot.keyboards.user_kbs import (
    main_user_keyboard, user_inline_keyboard_for_frwd_msg)
from src.app.utils import (
    check_user_telegram_id_in_db, get_user_id_and_token_by_telegram_id,
    get_user_pin_notes)
from src.app.services.user_service import UserService
from bot.create_bot import bot


user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    if not await check_user_telegram_id_in_db(message.from_user.id):
        service = UserService()
        await service.create_new_user(message.from_user.id, False)
    user_id, user_token = await get_user_id_and_token_by_telegram_id(
        message.from_user.id)
    await message.answer(
        'Выберите действие:',
        reply_markup=main_user_keyboard(user_id, user_token))


@user_router.message(
    lambda message: message.text in ['Показать закрепленные заметки'])
async def handle_button_press(message: types.Message):
    user_id = await get_user_id_and_token_by_telegram_id(message.from_user.id)
    user_pin_notes = await get_user_pin_notes(user_id[0])
    for obj in user_pin_notes:
        await bot.send_message(message.from_user.id, obj.text)
    await message.delete()


@user_router.message()
async def handle_forwarded_message(message: types.Message):
    current_msg_id = message.message_id
    try:
        tg_canal_name = message.forward_from_chat.username
        is_tg_canal_name = True
        if tg_canal_name is None:
            tg_canal_name = message.forward_from_chat.id
            is_tg_canal_name = False
        forw_msg_id = message.forward_from_message_id
    except Exception:
        pass
    user_id, user_token = await get_user_id_and_token_by_telegram_id(
        message.from_user.id)
    if message.forward_from:
        # Если сообщение переслано от пользователя
        user = message.forward_from
        await message.reply(
            text=f"Это пересланное сообщение от пользователя {user.full_name} (@{user.username}).",
            reply_markup=user_inline_keyboard_for_frwd_msg(
                user_id, user_token, tg_canal_name, forw_msg_id,
                current_msg_id, is_tg_canal_name))
    elif message.forward_from_chat:
        chat = message.forward_from_chat
        await message.reply(
            text=f"Это пересланное сообщение из чата {chat.title}.",
            reply_markup=user_inline_keyboard_for_frwd_msg(
                user_id, user_token, tg_canal_name, forw_msg_id,
                current_msg_id, is_tg_canal_name))
    else:
        await message.edit("Это не пересланное сообщение.")


@user_router.callback_query(F.data.startswith('delete_msg'))
async def send_random_person(call: CallbackQuery):
    msg_id = int(call.data.replace('delete_msg_', ''))
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=msg_id)
