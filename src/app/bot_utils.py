from bot.create_bot import bot
from core.config import settings

from src.app.constants import DESCRIPTION_BOT_MSG


async def send_message_for_admin(message):
    try:
        await bot.send_message(
            settings.ADMIN_TELEGRAM_ID, message)
    except Exception:
        pass


async def set_bot_description():
    await bot.set_my_description(DESCRIPTION_BOT_MSG)
    await bot.session.close()
