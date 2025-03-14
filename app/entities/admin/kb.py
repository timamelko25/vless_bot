from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data='statistics')
    kb.button(text="👤 Users", callback_data='handler_user')
    kb.button(text="🖥 Серверы", callback_data='handler_server')
    kb.button(text="🔑 Ключи", callback_data='handler_key')
    kb.button(text="Промокоды", callback_data='handler_promo')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_user() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Пополнить баланс", callback_data='upd_balance_user')
    kb.button(text="🔑 Добавить ключ пользователю",
              callback_data='add_key_user')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_server() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить сервер", callback_data='add_server_admin')
    kb.button(text="🗑 Удалить сервер", callback_data='del_server')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(2, 1)
    return kb.as_markup()


def admin_kb_key() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔑 Получить все ключи", callback_data='get_all_keys_admin')
    kb.button(text="🔑 Сгенерировать ключ", callback_data='generate_key_admin')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_promo() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Выпустить промокод", callback_data='gen_promo')
    kb.button(text="Получить все промокоды", callback_data='get_all_promo')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_current_key() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Удалить ключ", callback_data='del_key_admin')
    kb.button(text="✏️ Редактировать ключ", callback_data='edit_key_admin')
    kb.button(text="⚙️ Панель администратора", callback_data='admin_panel')
    kb.button(text="🏠 Главная страница", callback_data='home')
    kb.adjust(2)
    return kb.as_markup()


def admin_kb_confirm_add_key() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_add_key')
    kb.button(text="❌ Отмена", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_confirm_add_server() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_add_server')
    kb.button(text="❌ Отмена", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_confirm_upd_balance() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_upd_balance')
    kb.button(text="❌ Отмена", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def admin_kb_confirm_gen_promo() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data='confirm_gen_promo')
    kb.button(text="❌ Отмена", callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def admin_cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data='cancel')
    kb.adjust(1)
    return kb.as_markup()
