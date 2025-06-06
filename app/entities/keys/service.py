from urllib.parse import urlparse

from loguru import logger

from app.entities.servers.models import Server
from app.service.base import BaseService
from .schemas import KeyPayloadScheme, KeyScheme, PanelResponse, generate_vless_key
from .models import Key
from app.external_api.panel_api import (
    get_inbounds,
    add_client,
    delete_client,
    update_client,
    open_session,
)


class KeyService(BaseService):
    model = Key

    @classmethod
    async def generate_key(cls, data: KeyPayloadScheme, server: Server) -> KeyScheme:
        session, cookies = await open_session(url=server.domain)
        if not session:
            raise RuntimeError("Session not established")
        try:
            raw_response = await get_inbounds(session, cookies, url=server.domain)
            await add_client(session, cookies, url=server.domain, data=data)

            parsed = PanelResponse.model_validate(raw_response)
            dest = urlparse(server.domain)
            key = generate_vless_key(data, parsed, dest.netloc.split(":")[0])

            info = KeyScheme(
                **data.model_dump(),
                value=key,
                server_id=server.id,
            )

            return info
        except Exception as e:
            raise e
        finally:
            await session.close()

    @classmethod
    async def update_key(cls, data: KeyPayloadScheme, server: Server):
        session, cookies = await open_session(url=server.domain)
        if not session:
            raise RuntimeError("Session not established")

        try:
            info = await update_client(
                session, cookies, url=server.domain, data=data, uuid=data.id
            )
            info = await cls.update(
                filter_by={"id_panel": data.id},
                expires_at=str(data.expiryTime),
                status=data.status,
            )

            logger.info(f"Key successfully updated {data.email}")
            return info

        except Exception as e:
            logger.error(f"Error during updating key func {e}")
            return {}
        finally:
            await session.close()

    @classmethod
    async def delete_key(cls, uuid: str, server: Server, inboundId: str = "1") -> bool:
        session, cookies = await open_session(url=server.domain)
        if not session:
            raise RuntimeError("Session not established")

        try:
            await delete_client(
                session, cookies, url=server.domain, inboundId=inboundId, uuid=uuid
            )

            await cls.delete(id_panel=uuid)

            logger.info(f"Key deleted successfully {uuid} from db")
            return True

        except Exception as e:
            logger.error(f"Error while delete key {e}")
            return False

        finally:
            await session.close()
