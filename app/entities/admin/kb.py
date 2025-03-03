from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Statistics", callback_data='statistics')
    kb.button(text="User actions", callback_data='handler_user')
    kb.button(text="Server action", callback_data='handler_server')
    kb.button(text="Generate Key", callback_data='generate_key')
    kb.button(text="Main page", callback_data='home')
    kb.adjust(1, 2, 1)
    return kb.as_markup()


def admin_kb_user() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Update balance to user", callback_data='upd_balance_user')
    kb.button(text="Admin panel", callback_data='admin_panel')
    kb.button(text="Main page", callback_data='home')
    kb.adjust(2, 1, 1)
    return kb.as_markup()

def admin_kb_server() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Add new server", callback_data='add_server')
    kb.button(text="Delete exist server", callback_data='del_server')
    kb.button(text="Admin panel", callback_data='admin_panel')
    kb.button(text="Main page", callback_data='home')
    kb.adjust(2,1)
    return kb.as_markup()  

def admin_kb_confirm() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Accept", callback_data='confirm')
    kb.button(text="Cancel", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()

def admin_cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Cancel", callback_data='cancel')
    kb.adjust(1)
    return kb.as_markup()