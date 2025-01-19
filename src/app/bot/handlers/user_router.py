from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message

# from bot.create_bot import bot
from bot.keyboards.user_kbs import main_user_keyboard
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
    try:
        print(message.forward_from_chat.username)
        print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
        print(message.forward_from_message_id)
    except Exception:
        pass
    if message.forward_from:
        # Если сообщение переслано от пользователя
        user = message.forward_from
        await message.reply(f"Это пересланное сообщение от пользователя {user.full_name} (@{user.username}).")
    elif message.forward_from_chat:
        # Если сообщение переслано от чата
        chat = message.forward_from_chat
        # print(chat)
        # print(message.forward_from_chat)

        await message.reply(f"Это пересланное сообщение из чата {chat.title}.")
    else:
        await message.reply("Это не пересланное сообщение.")
    await message.reply(
        'Category: asdasdasdasdasdasdasdasdasdasdasd; \n'     
        'Текст заметки: https://t.me/dotdgif/17613')

    # msg = await bot.get_chat_history(1001718060030, 29858)