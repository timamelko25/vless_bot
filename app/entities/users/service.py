from app.service.base import BaseService
from .models import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection
from loguru import logger


class UserService(BaseService):
    model = User

    @classmethod
    @connection()
    async def update_balance(cls, session: AsyncSession, telegram_id, balance):
        user = await cls.find_one_or_none(telegram_id=telegram_id)

        if not user:
            logger.warning("User not found while updating balance")

        info = await cls.update(
            filter_by={"telegram_id": f"{telegram_id}"},
            balance=(balance + user.balance)
        )

        await session.flush()
        return info
