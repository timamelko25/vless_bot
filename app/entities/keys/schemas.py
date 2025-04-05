from pydantic import BaseModel


class KeyPayloadScheme(BaseModel):
    id: str
    email: str
    limitIp: int
    totalGb: int
    expiryTime: int
    status: bool | None = None
