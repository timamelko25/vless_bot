from typing import List

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.config import settings


def home_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Главное меню", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def main_inline_kb(user_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Профиль", callback_data='get_profile')
    kb.button(text="🔑 Получить ключ", callback_data='start_getting_key')
    kb.button(text="🛠️ Установка ключа", callback_data='get_help')
    if user_id in settings.ADMINS_LIST:
        kb.button(text="⚙️ Admin Panel", callback_data='admin_panel')

    kb.adjust(1)
    return kb.as_markup()


def profile_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Пополнение баланса", callback_data='top_up')
    kb.button(text="🎉 Промокод", callback_data='promocode')
    kb.button(text="🔑 Мои ключи", callback_data='get_all_keys')
    kb.button(text="⬅️ Назад", callback_data='home')
    kb.adjust(1, 2, 1)
    return kb.as_markup()


def get_key_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Пополнение баланса", callback_data='top_up')
    kb.button(text="⬅️ Назад", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def servers_inline_kb(servers: List) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for server in servers:
        kb.button(text=f'🌐 {server}', callback_data='get_key')
    kb.button(text='🏠 Главное меню', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def prices_reply_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="100 💸")
    kb.button(text="250 💸")
    kb.button(text="500 💸")
    return kb


def keys_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="IOS", callback_data='get_info_ios')
    kb.button(text="Android", callback_data='get_info_android')
    kb.button(text="MacOS", callback_data='get_info_mac')
    kb.button(text="Windows", callback_data='get_info_win')
    kb.button(text="Главное меню", callback_data='home')

    kb.adjust(2, 2, 1)
    return kb.as_markup()


def kb_confirm_upd() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_add_balance')
    kb.button(text="❌ Отмена", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def cancel_inline_kb(price: float) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f"Оплатить {price}₽", pay=True)
    kb.button(text="❌ Отмена", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()

def promocode_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Попробовать еще раз", callback_data='promocode')
    kb.button(text="🏠 Главное меню", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()