from contextlib import asynccontextmanager

# from app.bot.handlers.user_router import user_router
from aiogram.types import Update
from fastapi import FastAPI, Request

from api.routers import user_router_api
from bot.handlers.user_router import user_router
from bot.create_bot import bot, dp, stop_bot, start_bot
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # dp.include_router(user_router)
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


@app.post("/webhook")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
app.include_router(user_router_api)
