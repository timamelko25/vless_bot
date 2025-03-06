from pydantic import BaseModel, Field

class NewUserScheme(BaseModel):
    telegram_id: str
    username: str | None
    first_name: str | None
    last_name: str | None