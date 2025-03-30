from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

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
        info = await cls.delete(name=server_name)
        await session.flush()
        return info