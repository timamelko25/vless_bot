from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def keys_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='IOS', callback_data='get_info_ios')
    kb.button(text='Android', callback_data='get_info_android')
    kb.button(text='Windows', callback_data='get_info_win')
    kb.button(text='MacOS', callback_data='get_info_mac')
    kb.button(text='Главное меню', callback_data='home')
    kb.adjust(2,2,1)
    return kb.as_markup()