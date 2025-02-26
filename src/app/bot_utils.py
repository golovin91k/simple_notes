from core.config import settings
from bot.create_bot import bot


async def send_message_for_admin(message):
    try:
        await bot.send_message(
            settings.ADMIN_TELEGRAM_ID, message)
    except Exception:
        pass
