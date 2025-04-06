from typing import Dict

from pydantic import BaseModel



class NewUserScheme(BaseModel):
    telegram_id: str
    username: str | None
    first_name: str | None
    last_name: str | None
    refer_id: str | None


