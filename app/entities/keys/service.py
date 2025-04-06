from typing import Dict
import json

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.servers.models import Server
from app.service.base import BaseService, connection
from .schemas import KeyPayloadScheme, KeyScheme
from .models import Key
from .panel_api import get_inbounds, add_client, delete_client, update_client


class KeyService(BaseService):
    model = Key

    @classmethod
    async def generate_key(cls, data: KeyPayloadScheme, server: Server) -> KeyScheme:
        info = await get_inbounds(url=server.domain)
        await add_client(url=server.domain, data=data)

        key = info.get("obj")
        stream_settings = key[0].get("streamSettings", {})
        stream_settings = json.loads(stream_settings)

        start = len("https://")
        end = server.domain.find(":8443")
        dest = server.domain[start:end]

        type = stream_settings.get("network")
        security = stream_settings.get("security")
        realitySettings = stream_settings.get("realitySettings", {})

        serverName = realitySettings.get("serverNames")
        shortIds = realitySettings.get("shortIds")
        settings_panel = realitySettings.get("settings", {})
        publicKey = settings_panel.get("publicKey")
        fp = settings_panel.get("fingerprint")

        key = f"vless://{data.id}@{dest}:443?type={type}&security={security}&pbk={publicKey}&fp={fp}&sni={serverName[0]}&sid={shortIds[0]}&spx=%2F&flow=xtls-rprx-vision#{data.email}"

        info = KeyScheme(
            **data.model_dump(),
            value=key,
            server_id=server.id,
            )

        return info

    @classmethod
    @connection()
    async def update_key(
        cls, session: AsyncSession, data: KeyPayloadScheme, server: Server
    ):
        try:
            info = await update_client(url=server.domain, data=data, uuid=data.id)
            info = await cls.update(
                filter_by={"id_panel": data.id},
                expires_at=str(data.expiryTime),
                status=data.status,
            )

            await session.flush()
            logger.info(f"Key successfully updated {data.email}")
            return info

        except Exception as e:
            logger.error(f"Error during updating key func {e}")
            return {}

    @classmethod
    @connection()
    async def delete_key(
        cls, session: AsyncSession, uuid: str, server: Server, inboundId: str = "1"
    ) -> bool:
        try:
            await delete_client(url=server.domain, inboundId=inboundId, uuid=uuid)

            await cls.delete(id_panel=uuid)

            await session.flush()
            logger.info(f"Key successfully deleted {uuid}")
            return True

        except Exception as e:
            logger.error(f"Error while delete key {e}")
            return False
