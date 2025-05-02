from typing import List

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings


def home_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Главное меню", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def main_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Профиль", callback_data="get_profile")
    kb.button(text="🔑 Получить ключ", callback_data="start_getting_key")
    kb.button(text="🛠️ Установка ключа", callback_data="get_help")
    if user_id in settings.ADMINS_LIST:
        kb.button(text="⚙️ Admin Panel", callback_data="admin_panel")
    kb.button(text="FAQ", callback_data="FAQ")
    kb.adjust(1)
    return kb.as_markup()


def profile_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Пополнение баланса", callback_data="top_up")
    kb.button(text="🎉 Промокод", callback_data="promocode")
    kb.button(text="🔑 Мои ключи", callback_data="get_all_keys")
    kb.button(text="⬅️ Назад", callback_data="home")
    kb.adjust(1, 2, 1)
    return kb.as_markup()


def top_up_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Пополнение баланса", callback_data="top_up")
    kb.button(text="⬅️ Назад", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def get_key_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Получить ключ", callback_data="start_getting_key")
    kb.button(text="Главное меню", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def servers_kb(servers: List) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for server in servers:
        kb.button(text=f"🌐 {server}", callback_data=f"get_key_confirm:{server}")
    kb.button(text="🏠 Главное меню", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def instructions_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="IOS", url="https://telegra.ph/Ustanovka-klyucha-IOS-05-02")
    kb.button(text="Android", url="https://telegra.ph/Ustanovka-klyucha-Android-05-02")
    kb.button(text="MacOS", url="https://telegra.ph/Ustanovka-klyucha-IOS-05-02")
    kb.button(text="Windows", url="https://telegra.ph/Ustanovka-klyucha-Windows-05-02")
    kb.button(text="Главное меню", callback_data="home")

    kb.adjust(2, 2, 1)
    return kb.as_markup()


def del_key_kb(key_email: str, server_name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="❌ Удалить ключ", callback_data=f"confirm_del:{key_email}:{server_name}"
    )
    kb.adjust(1)
    return kb.as_markup()


def kb_confirm_upd() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="confirm_add_balance")
    kb.button(text="❌ Отмена", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def kb_confirm_get_key(balance: float) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="get_key")
    if balance < 150:
        kb.button(text="💳 Пополнение баланса", callback_data="top_up")
    kb.button(text="Главное меню", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def payment_kb(price: float) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f"Оплатить {price}₽", pay=True)
    kb.button(text="❌ Отмена", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def promocode_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Попробовать еще раз", callback_data="promocode")
    kb.button(text="🏠 Главное меню", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()
