import os

from loguru import logger

from typing import List

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMINS_LIST: List[int]
    #PROVIDER_TOKEN: str
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    
    
    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_PORT: int
    PG_NAME: str
    
    REDIS_USER: str
    REDIS_USER_PASSWORD: str
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    
    VLESS_HOST: str
    VLESS_PORT: int
    VLESS_WEBBASEPATH: str

    VLESS_USERNAME: str
    VLESS_PASSWORD: str
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )
    
    
    def get_pg_url(self):
        return (
            f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASSWORD}@"
            f"{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}"
        )
        
    def get_redis_url(self):
        return (
            f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )
    
    def get_vpn_url(self):
        return (
            f"https://{self.VLESS_HOST}:{self.VLESS_PORT}/{self.VLESS_WEBBASEPATH}"
            )
        
settings = Settings()

PG_URL = settings.get_pg_url()
REDIS_URL = settings.get_redis_url()

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=RedisStorage.from_url(REDIS_URL))
admins = settings.ADMINS_LIST

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# scheduler = AsyncIOScheduler(timezone='Europe/Moscow')