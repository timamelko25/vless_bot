from pydantic import BaseModel, Field, ConfigDict

from app.entities.keys.models import Key

class UserScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    telegram_id: int
    username: str
    balance: float = 0

    
class ServerScheme(BaseModel):
    name: str
