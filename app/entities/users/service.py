from typing import List
import uuid
from datetime import datetime, timedelta, timezone

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.keys.models import Key
from app.entities.servers.service import ServerService
from app.service.base import BaseService
from app.database import connection
from app.entities.keys.service import KeyService
from app.entities.promocodes.service import PromocodeService
from .schemas import KeyScheme
from .models import User


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
    
    @classmethod
    @connection()
    async def update_balance_and_count_refer(cls, session: AsyncSession, telegram_id: str, balance: float):
        user = await cls.find_one_or_none(telegram_id=telegram_id)

        if not user:
            logger.warning("User not found while updating balance")

        info = await cls.update(
            filter_by={"telegram_id": f"{telegram_id}"},
            balance=(balance + user.balance),
            count_refer = (user.count_refer + 1)
        )

        await session.flush()
        return info

    @classmethod
    @connection()
    async def update_count_refer(cls, session: AsyncSession, telegram_id: str):
        user = await cls.find_one_or_none(telegram_id=telegram_id)

        if not user:
            logger.error(
                f"User {telegram_id} not found while updating balance")

        info = await cls.update(
            filter_by={"telegram_id": telegram_id},
            count_refer=(user.count_refer + 1)
        )

        await session.flush()
        return info

    @classmethod
    @connection()
    async def create_key(cls, session: AsyncSession, telegram_id: str, server: str, data: dict = None) -> dict:
        user = await cls.find_one_or_none(telegram_id=telegram_id)
        server = await ServerService.find_one_or_none(name=server)
        if data is None:
            # получение времени по UNIX timestamp (с 1970 года) в миллисекундах
            current_time = datetime.now(timezone.utc)
            new_time = current_time + timedelta(days=30)
            date = int(new_time.timestamp() * 1000)
            
            data = {
                "id": str(uuid.uuid4()),
                "email": str(uuid.uuid4()).replace('-', '')[:10],
                "limitIp": 3,
                "totalGB": 107374182400, # 100gb in bits
                # для пробного + 3 сделать
                "expiryTime": str(date),
            }

        info = await KeyService.generate_key(data, server)

        new_key = Key(
            user_id=str(user.id),
            server_id=info.get('server_id'),
            user=user,
            server=server,
            id_panel=info.get('id'),
            value=info.get('key_value'),
            expires_at=info.get('expiryTime'),
            email=info.get('email'),
            status=True
        )

        user.keys.append(new_key)
        session.add(new_key)

        await cls.update(
            filter_by={"telegram_id": telegram_id},
            balance=user.balance - 150
        )

        await session.flush()
        return new_key.to_dict()

    @classmethod
    @connection()
    async def update_key():
        pass

    @classmethod
    @connection()
    async def delete_key():
        pass
    
    @classmethod
    @connection()
    async def get_all_keys(cls, session: AsyncSession, telegram_id: str) -> List:
        user = await cls.find_one_or_none(telegram_id=telegram_id)
        
        if not user:
            logger.error(
                f"User {telegram_id} not found while getting keys")
            
        await session.flush()
        return user.keys


    @classmethod
    @connection()
    async def get_promocode(cls, session: AsyncSession, telegram_id: str, code: str):
        promocode = await PromocodeService.find_one_or_none(code=code)
        
        if promocode.count > 0:
            await cls.update_balance(
                telegram_id=telegram_id,
                balance=promocode.bonus
                )
            info = await PromocodeService.update_count(code=promocode.code)
            await session.flush()
            return info
        
        return None
    
    @classmethod
    @connection()
    async def find_min_date_expire(cls, session: AsyncSession, telegram_id: str):
        keys = await cls.get_all_keys(telegram_id=telegram_id)
        if keys:
            date = 10000000000000
            for key in keys:
                date = min(int(key.expires_at), date)
                
            date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
            return date
        return None