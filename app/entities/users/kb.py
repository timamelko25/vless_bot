from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.config import settings


def main_inline_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Профиль", callback_data='get_profile')
    kb.button(text="Получить ключ", callback_data='get_server')
    if user_id in settings.ADMINS_LIST:
        kb.button(text="Admin Panel", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def profile_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Пополнение баланса", callback_data='top_up')
    kb.button(text="Промокод", callback_data='promocode')
    kb.button(text='Все ключи', callback_data='get_all_keys')
    kb.button(text="Назад", callback_data='back')
    kb.adjust(1,2,1)
    return kb.as_markup()


def servers_inline_kb(servers: list):
    kb = InlineKeyboardBuilder()
    for server in servers:
        kb.row(
            InlineKeyboardButton(text=f'{server}', callback_data='get_key')
        )
    kb.row(
        InlineKeyboardButton(text='Главное меню', callback_data='home')
    )
    kb.adjust(1)
    return kb.as_markup()


def keys_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='IOS', callback_data='get_info_ios')
    kb.button(text='Android', callback_data='get_info_android')
    kb.button(text='Windows', callback_data='get_info_win')
    kb.button(text='MacOS', callback_data='get_info_mac')
    kb.button(text='Главное меню', callback_data='home')
    kb.adjust(2,2,1)
    return kb.as_markup()
