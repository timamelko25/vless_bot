from typing import Dict
import json

from app.service.base import BaseService
from .models import Key
from .panel_api import get_inbounds, add_client


class KeyService(BaseService):
    model = Key

    # gen key
    @classmethod
    async def generate_key(cls, data, server) -> Dict:
        # server = await ServerService.find_one_or_none(name=server)

        data = {
            "id": data.get('id'),
            "email": data.get('email'),
            "limitIp": data.get('limitIp'),
            "totalGB": data.get('totalGB'),
            "expiryTime": data.get('expiryTime'),
        }

        info = await get_inbounds(url=server.domain)
        await add_client(data, url=server.domain)

        key = info.get('obj')
        stream_settings = key[0].get('streamSettings', {})
        stream_settings = json.loads(stream_settings)
        externalProxy = stream_settings.get('externalProxy')
        dest = externalProxy[0].get('dest')
        type = stream_settings.get('network')
        security = stream_settings.get('security')
        realitySettings = stream_settings.get('realitySettings', {})
        serverName = realitySettings.get('serverNames')
        shortIds = realitySettings.get('shortIds')
        settings_panel = realitySettings.get('settings', {})
        publicKey = settings_panel.get('publicKey')
        fp = settings_panel.get('fingerprint')

        key = f"vless://{data.get('id')}@{dest}:443?type={type}&security={security}&pbk={publicKey}&fp={fp}&sni={serverName[0]}&sid={shortIds[0]}&spx=%2F&flow=xtls-rprx-vision#{data.get('email')}"

        data.update(
            {
                "key_value": key,
                "server_id": server.id
            }
        )

        return data

    # upd key
    # del key
