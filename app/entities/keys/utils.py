import string
import random
import aiohttp
import json
import uuid

from loguru import logger

from app.config import settings

url_panel = settings.get_vpn_url()


async def open_session(url=url_panel):
    '''Открыть сессию с панелью для запросов'''

    data = {
        "username": settings.VLESS_USERNAME,
        "password": settings.VLESS_PASSWORD
    }

    path = '/login'
    session = aiohttp.ClientSession()

    try:
        async with session.post(url=url+path, json=data, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                return session
            else:
                logger.warning(f"Login failed {response.status}")
                await session.close()
                return {}
    except Exception as e:
        logger.error(f"Error login: {e}")
        await session.close()
        return {}


async def get_inbounds(url=url_panel) -> dict:
    '''Получить список всех подключений по протоколам'''

    path = '/panel/api/inbounds/list'

    session = await open_session()
    if session is None:
        return {}
    data = {}

    try:
        async with session.get(url=url+path, ssl=False) as response:
            if response.status == 200:
                data = await response.text()
                data = data.replace('\\n', '')
                await session.close()
                return json.dumps(data)
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


async def add_client(data, url=url_panel):
    '''Добавить нового клиента'''

    path = '/panel/api/inbounds/addClient'
    
    payload = {
        "id": 1,
        "settings": json.dumps({
            "clients": [
                {
                    "id": str(uuid.uuid4()),
                    "flow": "xtls-rprx-vision",
                    "email": str(uuid.uuid4()).replace('-', '')[:10],
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

    session, cookies = await open_session()
    if session is None:
        return {}
    
    data = {}

    try:
        async with session.post(url=url+path, headers=headers, cookies=cookies, data=payload, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                await session.close()
                return data
            else:
                logger.warning(f"Failed to add client {response.status}")
                await session.close()
                return {}
    except Exception as e:
        logger.error(f"Error add client: {e}")
        await session.close()
        return {}


async def update_inbound(session, id, payload, url=url_panel):
    '''Обновить информацию о пользователе по ID'''

    path = '/panel/api/inbounds/updateClient/'

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

