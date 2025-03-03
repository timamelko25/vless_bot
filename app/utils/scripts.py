import requests

import aiohttp, asyncio

from decouple import config

url = f"https://{config('VLESS_HOST')}:{config('VLESS_PORT')}/{config('VLESS_WEBBASEPATH')}"

async def open_session(url):
    data = {
        "username": config('VLESS_USERNAME'),
        "password": config('VLESS_PASSWORD')
        }

    path = '/login'
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url=url+path, json=data, ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    print(data)
                    return session
                else:
                    print(f"Login failed {response.status}")
                    return None
        except Exception as e:
            print(f"Error login: {e}")
            return None
    
async def get_inbounds(session, url):
    path = '/panel/api/inbounds/list'
    
    try:
        async with session.get(url=url+path, ssl=False) as response:
            if response.status_code == 200:
                data = await response.json()
                return data
            else:
                print(f"Failed to fetch inbounds {response.status_code}")
                return None
    except Exception as e:
        print(f"Error inbound: {e}")
        return None

async def get_inbound_id(session, url, id):
    path = '/panel/api/inbounds/get/'
    
    try:
        async with session.get(url=url+path+id, ssl=False) as response:
            if response.status_code == 200:
                data = await response.json()
                return data
            else:
                print(f"Failed to fetch id inbound {response.status_code}")
    except Exception as e:
        print(f"Error id inbound: {e}")
        return None
    

async def add_client(session, url, payload):
    path = '/panel/api/inbounds/addClient'
    
    try:
        async with session.post(url=url+path, json=payload, ssl=False) as response:
            if response.status_code == 200:
                data = await response.json()
                return data
            else:
                print(f"Failed to add client {response.status_code}")
                return None
    except Exception as e:
        print(f"Error add client: {e}")
        return None
    
async def update_inbound(session, url, id, payload):
    path = '/panel/api/inbounds/updateClient/'
    
    try:
        async with session.post(url=url+path+id, json=payload, ssl=False) as response:
            if response.status_code == 200:
                data = await response.json()
                return data
            else:
                print(f"Failed to update client inbound {response.status_code}")
                return None
    except Exception as e:
        print(f"Error update client inbound {e}")
        return None