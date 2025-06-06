from typing import List

from app.entities.keys.service import KeyService
from app.service.base import BaseService
from .models import Server


class ServerService(BaseService):
    model = Server

    @classmethod
    async def get_servers_names(cls) -> List[str]:
        try:
            servers = await cls.find_all()

            return [server.name for server in servers]
        except Exception as e:
            raise e

    @classmethod
    async def delete_server(cls, server_name: str):
        try:
            server = await cls.find_one_or_none(name=server_name)
            if not server:
                return 0
            await KeyService.delete(server_id=server.id)

            info = await cls.delete(name=server_name)
            return info
        except Exception as e:
            raise e
