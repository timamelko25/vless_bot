import os
from typing import List

from loguru import logger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import create_database, database_exists


class Settings(BaseSettings):
    BOT_TOKEN: str
    PROVIDER_TOKEN: str
    ADMINS_LIST: List[int]
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"

    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_PORT: int
    PG_NAME: str

    PG_JOBS_USER: str
    PG_JOBS_PASSWORD: str
    PG_JOBS_HOST: str
    PG_JOBS_PORT: int
    PG_JOBS_NAME: str

    REDIS_USER: str
    REDIS_USER_PASSWORD: str
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    VHOST: str

    BASE_URL: str

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

    def get_pg_jobs_url(self):
        return (
            f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@"
            f"{self.PG_JOBS_HOST}:{self.PG_JOBS_PORT}/{self.PG_JOBS_NAME}"
        )

    def get_redis_url(self):
        return (
            f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    def get_rabbitmq_url(self):
        return (
            f"amqp://{self.RABBITMQ_USERNAME}:{self.RABBITMQ_PASSWORD}@"
            f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.VHOST}"
        )

    def get_webhook(self):
        return f"{self.BASE_URL}/webhook"


settings = Settings()  # type: ignore

PG_URL = settings.get_pg_url()
PG_JOBS_URL = settings.get_pg_jobs_url()
REDIS_URL = settings.get_redis_url()

bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=RedisStorage.from_url(REDIS_URL))
admins = settings.ADMINS_LIST

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(
    log_file_path,
    format=settings.FORMAT_LOG,
    level="INFO",
    rotation=settings.LOG_ROTATION,
)

broker = RabbitBroker(url=settings.get_rabbitmq_url())


Base_jobs = declarative_base()


scheduler = AsyncIOScheduler(
    jobstores={"default": SQLAlchemyJobStore(url=settings.get_pg_jobs_url())},
    timezone="Europe/Moscow",
)
