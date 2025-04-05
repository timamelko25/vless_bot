from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.keys.service import KeyService
from app.service.base import BaseService
from app.database import connection
from .models import Server


class ServerService(BaseService):
    model = Server

    @classmethod
    @connection()
    async def get_servers_list(cls, session: AsyncSession) -> List[str]:
        servers = await cls.find_all()
        info = [server.name for server in servers]

        return info

    @classmethod
    @connection()
    async def delete_server(cls, session: AsyncSession, server_name: str):
        server = await cls.find_one_or_none(name=server_name)
        await KeyService.delete(server_id=server.id)

        info = await cls.delete(name=server_name)
        await session.flush()
        return info
