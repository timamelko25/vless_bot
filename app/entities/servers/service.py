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
