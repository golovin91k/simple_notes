from contextlib import asynccontextmanager
import os

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles


from api.user_router_api import user_router_api
from bot.create_bot import bot, dp, stop_bot, start_bot
from bot.handlers.user_router_bot import user_router_bot
from constants import REBOOT_MESSAGE
from core.config import settings, BASE_DIR
from src.app.logger_config import logger
from utils import create_user_admin, send_message_for_all_users
from bot_utils import set_bot_description


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Бот запущен')
    await set_bot_description()
    try:
        await create_user_admin()
        logger.info('Создан админ')
    except Exception:
        logger.exception('Произошла ошибка или админ уже создан')
    dp.include_router(user_router_bot)
    await start_bot()
    webhook_url = settings.get_webhook_url
    await bot.set_webhook(
        url=webhook_url, allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True)
    # await send_message_for_all_users(REBOOT_MESSAGE)
    yield
    await bot.delete_webhook()
    await stop_bot()


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None)
app.mount(
    f'/{settings.BOT_PATH}/statics', StaticFiles(
        directory=os.path.join(BASE_DIR, 'src/statics')), name='statics')


@app.post('/{BOT_PATH}/webhook')
async def webhook(request: Request) -> None:
    try:
        update = Update.model_validate(
            await request.json(), context={'bot': bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.exception(
            f'Возникла ошибка при отправке вебхука \n{e}')


app.include_router(user_router_api)
