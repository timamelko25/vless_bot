import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault

from loguru import logger

from app.config import bot, dp, admins
from app.entities.users.router import router as user_router
from app.entities.admin.router import router as admin_router

from sqlalchemy_utils import create_database, database_exists

from app.entities import *

async def set_commands():
    commands = [
        BotCommand(command='start', description='Main Menu'),
        BotCommand(command='profile', description='Profile'),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():

    await set_commands()

    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Bot started 🤯+💀')
        except:
            pass
    logger.info("Bot Started")


async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, f'︻デ══━一💥  Bot dead ')
    except:
        pass
    logger.error("Bot stopped")


async def main():

    dp.include_router(user_router)
    dp.include_router(admin_router)

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
