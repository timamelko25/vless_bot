from pydantic import BaseModel

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