from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from app.config import settings, bot

from .kb import admin_kb, admin_kb_confirm, admin_kb_server, admin_kb_user, admin_cancel_kb

from .utils import del_msg

router = Router()


class UpdateBalance(StatesGroup):
    telegram_id = State()
    balance = State()
    confirm = State()


@router.callback_query(F.data == 'cancel', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(
        text="Cancel operation",
        reply_markup=admin_kb()
        )

@router.callback_query(F.data == 'admin_panel', F.from_user.id.in_(settings.ADMINS_LIST))
async def start_admin(call: CallbackQuery):
    await call.answer("Welcome to admin panel")
    await call.message.edit_text(
        text="Вам разрешен доступ в админ-панель. Выберите необходимое действие.",
        reply_markup=admin_kb()
    )

@router.callback_query(F.data == 'statistics', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_stats(call: CallbackQuery):
    # сделать в сервисах пользователя и сервера функции для статистики
    stats = (
        "all users\n"
        "create tables\n"
        )
    await call.message.edit_text(
        text=stats,
        reply_markup=admin_kb()
        )
    
@router.callback_query(F.data == 'handler_user', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_user(call: CallbackQuery):
    await call.message.edit_text(
        text="Choose option",
        reply_markup=admin_kb_user()
        )
    
@router.callback_query(F.data == 'handler_server', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_user(call: CallbackQuery):
    await call.message.edit_text(
        text="Choose option",
        reply_markup=admin_kb_server()
        )
    
@router.callback_query(F.data == 'generate_key', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_generate_key(call: CallbackQuery):
    # logic ro generate key from panel
    key = '123'
    await call.message.edit_text(
        text=key,
        reply_markup=admin_kb()
        )

@router.callback_query(F.data == 'upd_balance_user', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_update_balance(call: CallbackQuery, state: FSMContext):
    msg = await call.message.answer(text="input telegram id", reply_markup=admin_cancel_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(UpdateBalance.telegram_id)

@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), UpdateBalance.telegram_id)
async def admin_get_tg_id(message: Message, state: FSMContext):
    try:
        telegram_id = message.text
        await state.update_data(telegram_id=telegram_id)
        await del_msg(message, state)
        msg = await message.answer(text="Enter updated balance", reply_markup=admin_cancel_kb())
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(UpdateBalance.balance)
    except ValueError:
        await message.answer(text="Error. Input number (user ID)")
        return

@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), UpdateBalance.balance)
async def admin_get_balance(message: Message, state: FSMContext):
    try:
        balance = message.text
        await state.update_data(balance=balance)
        await del_msg(message, state)
        
        data = await state.get_data()
        # make check on existing user with tg id
        
        text = (
            f"Check all fields\n\n"
            f"Telegram ID: {data['telegram_id']}\n"
            f"New balance: {data['balance']}\n"
            )
        msg = await message.answer(text=text, reply_markup=admin_kb_confirm())
        await state.update_data(last_msg_id=msg.id)
        await state.set_state(UpdateBalance.confirm)
    except ValueError:
        await message.answer(text="Error. Enter valid balance")
        return
    
@router.callback_query(F.data == 'confirm', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_confirm_update(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id =data['last_msg_id'])
    del data['last_msg_id']
    # User service update balance
    await call.message.answer(text="Updated successfully", reply_markup=admin_kb())