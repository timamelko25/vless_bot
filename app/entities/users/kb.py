from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.config import settings

def home_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🏠 Главное меню', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()

def main_inline_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Профиль", callback_data='get_profile')
    kb.button(text="🔑 Получить ключ", callback_data='get_server')
    if user_id in settings.ADMINS_LIST:
        kb.button(text="⚙️ Admin Panel", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def profile_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Пополнение баланса", callback_data='top_up')
    kb.button(text="🎉 Промокод", callback_data='promocode')
    kb.button(text="🔑 Все ключи", callback_data='get_all_keys')
    kb.button(text="⬅️ Назад", callback_data='home')
    kb.adjust(1, 2, 1)
    return kb.as_markup()


def servers_inline_kb(servers: list)  -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for server in servers:
        kb.button(text=f'🌐 {server}', callback_data='get_key')
    kb.button(text='🏠 Главное меню', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()

def prices_reply_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder(resize_keyboard=True)
    kb.button(text="100 💸")
    kb.button(text="250 💸")
    kb.button(text="500 💸")
    return kb

def kb_confirm_upd() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_add_balance')
    kb.button(text="❌ Отмена", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()