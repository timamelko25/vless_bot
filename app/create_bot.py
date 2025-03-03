# import logging

# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.storage.redis import RedisStorage

# from decouple import config

# from apscheduler.schedulers.asyncio import AsyncIOScheduler

# #from app.db_handler.service import PostgresHandler

# #pg_db = PostgresHandler(config('PG_LINK'))

# REDIS_URL = f"redis://{config('REDIS_USER')}:{config('REDIS_PASSWORD')}@{config('REDIS_HOST')}:{config('REDIS_PORT')}/{config('REDIS_DB')}"

# storage = RedisStorage.from_url(REDIS_URL)

# scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

# admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# bot = Bot(token=config('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# #dp = Dispatcher(storage=MemoryStorage()) #uses Ram with no db and if bot restart all current data lost

# dp = Dispatcher(storage=storage)
