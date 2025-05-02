from pydantic import BaseModel
from aiogram.types import InlineKeyboardMarkup


class MessageScheme(BaseModel):
    message: str
    telegram_id: int | None = None
    keyboard: InlineKeyboardMarkup | None = None
