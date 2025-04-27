import traceback

from loguru import logger
from aiogram.types import BotCommand, BotCommandScopeDefault, Update
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import uvicorn

from app.config import bot, dp, settings, broker, scheduler
from app.utils.logger_conf import setup_logging
from app.entities.users.router_start import router as user_router_start
from app.entities.users.router_pay import router as user_router_pay
from app.entities.keys.router_key_get import router as key_router_get
from app.entities.admin.router import router as admin_router
from app.broker.router_consumer import router as broker_router
from app.entities import *
from app.scheduler.scheduler import subscribe_30_day_expire


async def set_commands():
    commands = [
        BotCommand(command="start", description="Main Menu"),
        BotCommand(command="profile", description="Profile"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()
    dp.include_router(user_router_start)
    dp.include_router(user_router_pay)
    dp.include_router(key_router_get)
    dp.include_router(admin_router)

    for admin_id in settings.ADMINS_LIST:
        await bot.send_message(admin_id, "Bot started 🤯+💀")
    logger.info("Bot Started")


async def stop_bot():
    for admin_id in settings.ADMINS_LIST:
        await bot.send_message(admin_id, "︻デ══━一💥  Bot dead ")
    await bot.delete_webhook()
    logger.error("Bot stopped")


async def start_tracking():
    try:
        scheduler.add_job(
            func=subscribe_30_day_expire,
            trigger="interval",
            seconds=60,
            id="check_subscription",
            replace_existing=True,
            misfire_grace_time=300
        )
        if not scheduler.state:
            scheduler.start()
            logger.info("Scheduler started")
            
        logger.info(f"Active jobs: {scheduler.get_jobs()}")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Bot getting starting")
    await start_tracking()
    await broker.start()
    await start_bot()
    webhook_url = settings.get_webhook()
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    setup_logging()
    logger.success(f"Webhook set {webhook_url}")
    yield
    logger.info("Bot getting stopped")
    await broker.close()
    scheduler.shutdown()
    await stop_bot()


app = FastAPI(lifespan=lifespan)

app.include_router(broker_router)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    logger.info("Get request from webhook")
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        logger.info("Webhook status updated")
    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"Error from webhook: {e}\n {tb_str}")


@app.get("/test")
async def test():
    return {"status": "ok"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
