from typing import Dict

from pydantic import BaseModel



class NewUserScheme(BaseModel):
    telegram_id: str
    username: str | None
    first_name: str | None
    last_name: str | None
    refer_id: str | None


class KeyScheme(BaseModel):
    user_id: str
    user: Dict
    id_panel: str
    email: str
    value: str
    expires_at: str
