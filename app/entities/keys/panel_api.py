import aiohttp
import json
import uuid

from loguru import logger

from app.config import settings
from app.entities.keys.schemas import KeyPayloadScheme


async def open_session(url):
    """Открыть сессию с панелью для запросов"""

    data = {"username": settings.VLESS_USERNAME, "password": settings.VLESS_PASSWORD}

    path = "login"
    session = aiohttp.ClientSession()

    try:
        async with session.post(url=url + path, json=data, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                return session, response.cookies
            else:
                logger.warning(f"Login failed {response.status}")
                await session.close()
                return {}
    except Exception as e:
        logger.error(f"Error login: {e}")
        await session.close()
        return {}


async def get_inbounds(url: str) -> dict:
    """Получить список всех подключений по протоколам"""

    path = "panel/api/inbounds/list"

    session, cookies = await open_session(url)
    if session is None:
        logger.error("Can`t create session while get inbounds")
        return {}

    try:
        async with session.get(url=url + path, cookies=cookies, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                logger.info("Data from panel got successfully")
                await session.close()
                return data
            else:
                logger.warning(f"Failed to fetch inbounds {response.status}")
                await session.close()
                return {}
    except Exception as e:
        logger.error(f"Error inbound: {e}")
        await session.close()
        return {}


# async def get_inbound_id(session, id, url=url_panel) -> dict:
#     '''Получить информацию по подключения по ID'''

#     path = '/panel/api/inbounds/get/'
#     session = await open_session()
#     if session is None:
#         return {}
#     data = {}
#     try:
#         async with session.get(url=url+path+id, ssl=False) as response:
#             if response.status == 200:
#                 data = await response.json()
#                 return data
#             else:
#                 logger.warning(f"Failed to fetch id inbound {response.status}")
#                 return {}
#     except Exception as e:
#         logger.error(f"Error id inbound: {e}")
#         return {}


async def add_client(url: str, data: KeyPayloadScheme):
    """Добавить нового клиента"""

    path = "panel/api/inbounds/addClient"

    payload = {
        "id": 1,
        "settings": json.dumps(
            {
                "clients": [
                    {
                        "id": data.id,
                        "flow": "xtls-rprx-vision",
                        "email": data.email,
                        "limitIp": data.limitIp,
                        "totalGB": data.totalGb,
                        "expiryTime": data.expiryTime,
                        "enable": True,
                        "tgId": "",
                        "subId": str(uuid.uuid4()).replace("-", "")[:16],
                        "reset": 0,
                    }
                ]
            }
        ),
    }

    headers = {"Accept": "application/json"}

    session, cookies = await open_session(url)
    if session is None:
        logger.error("Can`t create session while adding client")
        return {}

    try:
        async with session.post(
            url=url + path, headers=headers, cookies=cookies, data=payload, ssl=False
        ) as response:
            if response.status == 200:
                info = await response.json()
                logger.info(f"New client added to panel {data.email}")
                await session.close()
                return info
            else:
                logger.warning(f"Failed to add client {response.status}")
                await session.close()
                return {}
    except Exception as e:
        logger.error(f"Error add client: {e}")
        await session.close()
        return {}


async def update_client(url: str, uuid: str, data: KeyPayloadScheme):
    """""Обновить информацию о клиенте по ID""" ""

    path = f"panel/api/inbounds/updateClient/{uuid}"

    payload = {
        "id": 1,
        "settings": json.dumps(
            {
                "clients": [
                    {
                        "id": data.id,
                        "flow": "xtls-rprx-vision",
                        "alterId": 0,
                        "email": data.email,
                        "limitIp": data.limitIp,
                        "totalGB": data.totalGb,
                        "expiryTime": data.expiryTime,
                        "enable": data.status,
                        "tgId": "",
                        "subId": "",
                    }
                ]
            }
        ),
    }

    headers = {"Accept": "application/json"}

    session, cookies = await open_session(url)
    if session is None:
        logger.error("Can`t create session while updating client")
        return {}

    try:
        async with session.post(
            url=url + path, headers=headers, cookies=cookies, data=payload, ssl=False
        ) as response:
            if response.status == 200:
                info = await response.json()
                logger.info(f"Client updated with new payload {payload}")
                await session.close()
                return info
            else:
                logger.warning(f"Failed to update client inbound {response.status}")
                await session.close()
                return {}
    except Exception as e:
        logger.error(f"Error update client inbound {e}")
        await session.close()
        return {}


async def delete_client(url: str, inboundId: str, uuid: str):
    """Удалить существующего клиента"""

    path = f"panel/api/inbounds/{inboundId}/delClient/{uuid}"

    headers = {"Accept": "application/json"}

    session, cookies = await open_session(url)
    if session is None:
        logger.error("Can`t create session while delete client")
        return {}

    try:
        async with session.post(
            url=url + path, headers=headers, cookies=cookies, ssl=False
        ) as response:
            if response.status == 200:
                info = await response.json()
                logger.info(f"Client {uuid} delete successfully from panel")
                await session.close()
                return info
            else:
                logger.warning(f"Failed to delete client from panel {uuid}")
                await session.close()
                return {}
    except Exception as e:
        logger.error(f"Error while deleting client {e}")
        return {}
