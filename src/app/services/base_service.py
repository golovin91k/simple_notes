from src.app.bot_utils import send_message_for_admin


class BaseService():
    async def send_message_for_admin(self, message):
        try:
            await send_message_for_admin(message)
        except Exception:
            pass
