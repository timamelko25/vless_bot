from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data='statistics')
    kb.button(text="👤 Users", callback_data='handler_user')
    kb.button(text="🖥 Серверы", callback_data='handler_server')
    kb.button(text="🔑 Ключи", callback_data='handler_key')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(1, 3, 1)
    return kb.as_markup()


def admin_kb_user() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Пополнить баланс", callback_data='upd_balance_user')
    kb.button(text="🔑 Добавить ключ", callback_data='add_key_user')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(2, 1, 1)
    return kb.as_markup()


def admin_kb_server() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить сервер", callback_data='add_server')
    kb.button(text="🗑 Удалить сервер", callback_data='del_server')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(2, 1)
    return kb.as_markup()


def admin_kb_key() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔑 Получить все ключи", callback_data='get_all_keys')
    kb.button(text="🔑 Сгенерировать ключ", callback_data='generate_key')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()

def admin_kb_current_key() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Удалить ключ", callback_data='del_key')
    kb.button(text="✏️ Редактировать ключ", callback_data='edit_key')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(2)
    return kb.as_markup()


def admin_kb_confirm_add() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_add')
    kb.button(text="❌ Отмена", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()

def admin_kb_confirm_upd() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_upd')
    kb.button(text="❌ Отмена", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def admin_cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data='cancel')
    kb.adjust(1)
    return kb.as_markup()
