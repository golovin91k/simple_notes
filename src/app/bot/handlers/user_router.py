from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.create_bot import bot
from bot.keyboards.user_kbs import main_keyboard

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    await message.answer(
        "Чем я могу помочь вам сегодня?",
        reply_markup=main_keyboard()
    )
