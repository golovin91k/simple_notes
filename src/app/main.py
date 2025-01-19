from contextlib import asynccontextmanager
import os

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from api.routers import user_router_api
from bot.handlers.user_router import user_router
from bot.create_bot import bot, dp, stop_bot, start_bot
from core.config import settings, BASE_DIR
from utils import create_user_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_user_admin()
    dp.include_router(user_router)
    await start_bot()
    webhook_url = settings.get_webhook_url
    await bot.set_webhook(
        url=webhook_url, allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True)
    yield
    await bot.delete_webhook()
    await stop_bot()


app = FastAPI(lifespan=lifespan)
app.mount(
    '/statics', StaticFiles(
        directory=os.path.join(BASE_DIR, 'src/statics')), name="statics")


@app.post("/webhook")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


app.include_router(user_router_api)
