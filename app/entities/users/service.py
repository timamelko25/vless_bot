from typing import Dict, List
import uuid
from datetime import datetime, timedelta, timezone

from loguru import logger

from app.entities.keys.models import Key
from app.entities.servers.service import ServerService
from app.service.base import BaseService
from app.entities.keys.service import KeyService
from app.entities.keys.schemas import KeyPayloadScheme
from app.entities.promocodes.service import PromocodeService
from app.database import async_session_maker
from .models import User


class UserService(BaseService):
    model = User

    @classmethod
    async def update_balance(cls, telegram_id: int, balance: float):
        user = await cls.find_one_or_none(telegram_id=telegram_id)

        if not user:
            logger.warning("User not found while updating balance")
            return

        info = await cls.update(
            filter_by={"telegram_id": telegram_id},
            balance=(balance + user.balance),
        )

        return info

    @classmethod
    async def update_balance_and_count_refer(cls, telegram_id: int, balance: float):
        user = await cls.find_one_or_none(telegram_id=telegram_id)

        if not user:
            logger.warning(f"User {telegram_id} not found while updating balance")
            return

        info = await cls.update(
            filter_by={"telegram_id": telegram_id},
            balance=(balance + user.balance),
            count_refer=(user.count_refer + 1),
        )

        return info

    @classmethod
    async def update_count_refer(cls, telegram_id: int):
        user = await cls.find_one_or_none(telegram_id=telegram_id)

        if not user:
            logger.error(f"User {telegram_id} not found while updating balance")
            return

        info = await cls.update(
            filter_by={"telegram_id": telegram_id},
            count_refer=(user.count_refer + 1),
        )
        logger.info(f"User {telegram_id} updated refers count")

        return info

    @classmethod
    async def create_key(
        cls,
        telegram_id: int,
        server_name: str,
        data: KeyPayloadScheme | None = None,
    ) -> Dict | None:
        async with async_session_maker() as session:
            user = await cls.find_one_or_none(telegram_id=telegram_id)
            if user is None:
                return
            server = await ServerService.find_one_or_none(name=server_name)
            if server is None:
                return

            if data is None:
                current_time = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                new_time = current_time + timedelta(days=30)
                date = int(new_time.timestamp() * 1000)

                data = KeyPayloadScheme(
                    id=str(uuid.uuid4()),
                    email=str(uuid.uuid4()).replace("-", "")[:10],
                    limitIp=3,
                    totalGb=107374182400,
                    expiryTime=str(date),
                )

            info = await KeyService.generate_key(data, server)
            if info is None:
                return

            new_key = Key(
                user_id=user.id,
                server_id=info.server_id,
                user=user,
                # server=server,
                id_panel=info.id,
                value=info.value,
                expires_at=info.expiryTime,
                email=info.email,
                status=True,
            )

            user.keys.append(new_key)
            session.add(new_key)

            await cls.update(
                filter_by={"telegram_id": telegram_id},
                balance=user.balance - 150,
            )

            await session.commit()
            return new_key.to_dict()

    # TODO: ???
    @classmethod
    async def update_key(
        cls,
        telegram_id: int,
        server_name: str,
        data: KeyPayloadScheme,
    ) -> bool:
        user = await cls.find_one_or_none(telegram_id=telegram_id)
        if user is None:
            return False
        server = await ServerService.find_one_or_none(name=server_name)
        if server is None:
            return False

        info = await KeyService.update_key(server=server, data=data)

        if info:
            logger.info(f"User {telegram_id} successfully update key")
            return True
        return False

    # TODO: ???
    @classmethod
    async def delete_key(cls, telegram_id: int, server_name: str, key_id: str) -> bool:
        user = await cls.find_one_or_none(telegram_id=telegram_id)
        if user is None:
            return False
        server = await ServerService.find_one_or_none(name=server_name)
        if server is None:
            return False

        info = await KeyService.delete_key(
            inboundId="1", uuid=key_id, server=server
        )  # TODO сделать выбор среди инбаундов
        
        if info:
            logger.info(
                f"User {user.telegram_id} successfully delete key {key_id}"
            )
            return True
        return False

    @classmethod
    async def get_all_keys(cls, telegram_id: int) -> List[Key] | None:
        user = await cls.find_one_or_none(telegram_id=telegram_id)

        if not user:
            logger.error(f"User {telegram_id} not found while getting keys")
            return None

        return user.keys

    @classmethod
    async def get_promocode(cls, telegram_id: int, code: str):
        async with async_session_maker() as session:
            promocode = await PromocodeService.find_one_or_none(code=code)
            user = await cls.find_one_or_none(telegram_id=telegram_id)

            if any(p.id == promocode.id for p in user.promocodes_activate):
                return False

            if promocode.count > 0:
                await cls.update_balance(
                    telegram_id=telegram_id,
                    balance=promocode.bonus,
                )

                info = await PromocodeService.update_count(code=promocode.code)

                user.promocodes_activate.append(promocode)
                session.add(user)
                logger.info(f"User {user.telegram_id} activated promo {promocode.code}")
                await session.commit()
                return info

            return None

    @classmethod
    async def find_min_date_expire(cls, telegram_id: int) -> str | None:
        keys = await cls.get_all_keys(telegram_id=telegram_id)
        if keys:
            date = 10000000000000
            for key in keys:
                date = min(int(key.expires_at), date)

            date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d"
            )
            return date
        return None

    @classmethod
    async def find_expiry_keys(cls, telegram_id: int) -> List[Key] | None:
        keys = await cls.get_all_keys(telegram_id=telegram_id)
        if not keys:
            return None
        expiry_keys = [key for key in keys if not key.status]
        return expiry_keys
