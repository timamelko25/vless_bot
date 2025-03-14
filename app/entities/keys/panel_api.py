import string
import random
import aiohttp
import json
import uuid

from loguru import logger

from app.config import settings


async def open_session(url):
    '''Открыть сессию с панелью для запросов'''

    data = {
        "username": settings.VLESS_USERNAME,
        "password": settings.VLESS_PASSWORD
    }

    path = 'login'
    session = aiohttp.ClientSession()

    try:
        async with session.post(url=url+path, json=data, ssl=False) as response:
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


async def get_inbounds(url) -> dict:
    '''Получить список всех подключений по протоколам'''

    path = 'panel/api/inbounds/list'

    session, cookies = await open_session(url)
    if session is None:
        return {}

    try:
        async with session.get(url=url+path, cookies=cookies, ssl=False) as response:
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


async def add_client(data, url):
    '''Добавить нового клиента'''

    path = 'panel/api/inbounds/addClient'

    payload = {
        "id": 1,
        "settings": json.dumps({
            "clients": [
                {
                    "id": data.get('id'),
                    "flow": "xtls-rprx-vision",
                    "email": data.get('email'),
                    "limitIp": data.get('limitIp'),
                    "totalGB": data.get('totalGB'),
                    "expiryTime": data.get('expiryTime'),
                    "enable": True,
                    "tgId": "",
                    "subId": str(uuid.uuid4()).replace('-', '')[:16],
                    "reset": 0
                }
            ]
        })
    }

    headers = {
        'Accept': 'application/json'
    }

    session, cookies = await open_session(url)
    if session is None:
        return {}

    try:
        async with session.post(url=url+path, headers=headers, cookies=cookies, data=payload, ssl=False) as response:
            if response.status == 200:
                info = await response.json()
                logger.info(f"New client added to panel {data.get('email')}")
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


async def update_inbound(session, id, payload, url):
    '''Обновить информацию о пользователе по ID'''

    path = 'panel/api/inbounds/updateClient/'

    headers = {
        'Accept': 'application/json'
    }

    session = await open_session()
    if session is None:
        return {}
    data = {}
    try:
        async with session.post(url=url+path+id, headers=headers, json=payload, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logger.warning(
                    f"Failed to update client inbound {response.status}")
                return {}
    except Exception as e:
        logger.error(f"Error update client inbound {e}")
        return {}
