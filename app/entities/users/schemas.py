from pydantic import BaseModel, Field

class NewUserScheme(BaseModel):
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None