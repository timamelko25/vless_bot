from typing import List, Union
from pydantic import BaseModel, field_validator
import json

from app.database import int_pk


class KeyPayloadScheme(BaseModel):
    id: str
    email: str
    limitIp: int
    totalGb: int
    expiryTime: str
    status: bool | None = None


class KeyScheme(BaseModel):
    id: str
    email: str
    limitIp: int
    totalGb: int
    expiryTime: str
    status: bool | None
    value: str
    server_id: int_pk


class PanelClientStat(BaseModel):
    id: int
    inboundId: int
    enable: bool
    email: str
    up: int
    down: int
    expiryTime: Union[int, str]
    total: int
    reset: int


class RealitySettingsSettings(BaseModel):
    publicKey: str
    fingerprint: str
    serverName: str | None
    spiderX: str | None


class RealitySettings(BaseModel):
    show: bool | None
    xver: int | None
    dest: str | None
    serverNames: List[str]
    privateKey: str | None
    minClient: str | None
    maxClient: str | None
    maxTimediff: int | None
    shortIds: List[str]
    settings: RealitySettingsSettings


class StreamSettings(BaseModel):
    network: str
    security: str
    realitySettings: RealitySettings

    @classmethod
    def from_json_str(cls, raw: str) -> "StreamSettings":
        try:
            return cls.model_validate(json.loads(raw))
        except Exception as e:
            raise ValueError(f"Invalid streamSettings JSON: {e}")


class InboundObject(BaseModel):
    id: int
    up: int
    down: int
    total: int
    remark: str
    enable: bool
    expiryTime: Union[int, str]
    clientStats: List[PanelClientStat]
    port: int
    protocol: str
    streamSettings: StreamSettings

    @field_validator("streamSettings", mode="before")
    @classmethod
    def parse_stream_settings(cls, v):
        if isinstance(v, str):
            return StreamSettings.from_json_str(v)
        return v


class PanelResponse(BaseModel):
    success: bool
    msg: str
    obj: List[InboundObject]


def generate_vless_key(data, panel: PanelResponse, dest: str) -> str:
    inbound = panel.obj[0]
    settings = inbound.streamSettings

    type_ = settings.network
    security = settings.security
    reality = settings.realitySettings

    pbk = reality.settings.publicKey
    fp = reality.settings.fingerprint
    sni = reality.serverNames[0]
    sid = reality.shortIds[0]

    return (
        f"vless://{data.id}@{dest}:443?"
        f"type={type_}&security={security}&pbk={pbk}&fp={fp}"
        f"&sni={sni}&sid={sid}&spx=%2F&flow=xtls-rprx-vision#{data.email}"
    )
