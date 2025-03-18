from loguru import logger
from aiogram.types import BotCommand, BotCommandScopeDefault, Update
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import uvicorn

from app.config import bot, dp, settings, broker
from app.entities.users.router_start import router as user_router_start
from app.entities.users.router_pay import router as user_router_pay
from app.entities.keys.router_key_get import router as key_router_get
from app.entities.admin.router import router as admin_router
from app.broker.router_consumer import router as broker_router
from app.entities import *


async def set_commands():
    commands = [
        BotCommand(command='start', description='Main Menu'),
        BotCommand(command='profile', description='Profile'),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():

    await set_commands()
    dp.include_router(user_router_start)
    dp.include_router(user_router_pay)
    dp.include_router(key_router_get)
    dp.include_router(admin_router)

    for admin_id in settings.ADMINS_LIST:
        try:
            await bot.send_message(admin_id, 'Bot started 🤯+💀')
        except:
            logger.error("Error to send start message")
    logger.info("Bot Started")


async def stop_bot():
    try:
        for admin_id in settings.ADMINS_LIST:
            await bot.send_message(admin_id, '︻デ══━一💥  Bot dead ')
    except:
        logger.error("Error to send dead message")
    await bot.delete_webhook()
    logger.error("Bot stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Bot getting starting")
    await broker.start()
    await start_bot()
    # enable broker, scheduler + job
    webhook_url = settings.get_webhook()
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    logger.success(f"Webhook set {webhook_url}")
    yield
    logger.info("Bot getting stopped")
    await broker.close()
    await stop_bot()
    # close broker, scheduler

app = FastAPI(lifespan=lifespan)

app.include_router(broker_router)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    logger.info("Get request from webhook")
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        logger.info("Обновление успешно обработано.")
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления с вебхука: {e}")


@app.get("/test")
async def test():
    return {"status": "ok"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
