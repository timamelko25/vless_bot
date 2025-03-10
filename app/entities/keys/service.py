from typing import Dict
import uuid
import json

from app.service.base import BaseService
from app.config import settings
from app.database import connection
from .models import Key
from .panel_api import get_inbounds, add_client


class KeyService(BaseService):
    model = Key

    # gen key
    @classmethod
    async def generate_key(cls, data) -> Dict:

        data = {
            "id": data.get('id'),
            "email": data.get('email'),
            "limitIp": data.get('limitIp'),
            "totalGB": data.get('totalGB'),
            "expiryTime": data.get('expiryTime'),
        }

        info = await get_inbounds()
        client = await add_client(data)

        key = info.get('obj')
        stream_settings = key[0].get('streamSettings', {})
        stream_settings = json.loads(stream_settings)
        type = stream_settings.get('network')
        security = stream_settings.get('security')
        realitySettings = stream_settings.get('realitySettings', {})
        serverName = realitySettings.get('serverNames')
        shortIds = realitySettings.get('shortIds')
        settings_panel = realitySettings.get('settings', {})
        publicKey = settings_panel.get('publicKey')
        fp = settings_panel.get('fingerprint')

        key = f"vless://{data.get('id')}@{settings.VLESS_HOST}:443?type={type}&security={security}&pbk={publicKey}&fp={fp}&sni={serverName[0]}&sid={shortIds[0]}&spx=%2F&flow=xtls-rprx-vision#{data.get('email')}"

        data.update(
            {
                "key_value": key
            }
        )

        return data

    # upd key
    # del key
