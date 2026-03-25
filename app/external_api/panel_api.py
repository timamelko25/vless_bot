import aiohttp
import asyncio
import json
import uuid

from loguru import logger

from app.config import settings
from app.entities.keys.schemas import KeyPayloadScheme

MAX_RETRIES = 3
RETRY_DELAY = 2

async def open_session(url: str):
    """Открыть сессию с панелью для запросов с ретраями"""

    data = {"username": settings.VLESS_USERNAME, "password": settings.VLESS_PASSWORD}
    path = "login"

    for attempt in range(1, MAX_RETRIES + 1):
        session = aiohttp.ClientSession()
        try:
            async with session.post(url=url + path, json=data, ssl=False) as response:
                if response.status == 200:
                    logger.success(f"Login successful on attempt {attempt}")
                    return session, response.cookies
                else:
                    logger.warning(f"Login failed (status={response.status}) on attempt {attempt}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Attempt {attempt} failed with error: {e}")

    logger.critical("All attempts to login failed.")
    return None, None


async def get_inbounds(session, cookies, url: str) -> dict:
    """Получить список всех подключений по протоколам"""

    path = "panel/api/inbounds/list"

    try:
        async with session.get(url=url + path, cookies=cookies, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                logger.info("Data from panel got successfully")
                return data
            else:
                logger.warning(f"Failed to fetch inbounds {response.status}")
                return {}
    except Exception as e:
        logger.error(f"Error inbound: {e}")
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


async def add_client(session, cookies, url: str, data: KeyPayloadScheme):
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

    try:
        async with session.post(
            url=url + path, headers=headers, cookies=cookies, data=payload, ssl=False
        ) as response:
            if response.status == 200:
                info = await response.json()
                logger.info(f"New client added to panel {data.email}")
                return info
            else:
                logger.warning(f"Failed to add client {response.status}")
                return {}
    except Exception as e:
        logger.error(f"Error add client: {e}")
        return {}


async def update_client(session, cookies, url: str, uuid: str, data: KeyPayloadScheme):
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

    try:
        async with session.post(
            url=url + path, headers=headers, cookies=cookies, data=payload, ssl=False
        ) as response:
            if response.status == 200:
                info = await response.json()
                logger.info(f"Client updated with new payload {payload}")
                return info
            else:
                logger.warning(f"Failed to update client inbound {response.status}")
                return {}
    except Exception as e:
        logger.error(f"Error update client inbound {e}")
        return {}


async def delete_client(session, cookies, url: str, inboundId: str, uuid: str):
    """Удалить существующего клиента"""

    path = f"panel/api/inbounds/{inboundId}/delClient/{uuid}"

    headers = {"Accept": "application/json"}

    try:
        async with session.post(
            url=url + path, headers=headers, cookies=cookies, ssl=False
        ) as response:
            if response.status == 200:
                info = await response.json()
                logger.info(f"Client {uuid} delete successfully from panel")
                return info
            else:
                logger.warning(f"Failed to delete client from panel {uuid}")
                return {}
    except Exception as e:
        logger.error(f"Error while deleting client {e}")
        return {}
