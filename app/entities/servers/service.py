from sqlalchemy.ext.asyncio import AsyncSession

from app.service.base import BaseService
from app.database import connection
from .models import Server


class ServerService(BaseService):
    model = Server

    @classmethod
    @connection()
    async def get_servers_list(cls, session: AsyncSession):
        servers = await cls.find_all()
        info = []
        for server in servers:
            info.append(server.name_in_bot)

        return info
