from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from app.config import settings, bot

from .kb import admin_kb, admin_kb_confirm_add, admin_kb_server, admin_kb_user, admin_kb_key, admin_cancel_kb, admin_kb_current_key, admin_kb_confirm_upd
from app.utils.utils import del_msg

from app.entities.keys.utils import add_client, get_inbounds

from loguru import logger

router = Router()


class UpdateBalance(StatesGroup):
    telegram_id = State()
    balance = State()
    confirm = State()


class NewKey(StatesGroup):
    email = State()
    limitIp = State()
    totalGB = State()
    expiryTime = State()
    confirm = State()


@router.callback_query(F.data == 'cancel', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        text="Cancel operation",
        reply_markup=admin_kb()
    )


@router.callback_query(F.data == 'admin_panel', F.from_user.id.in_(settings.ADMINS_LIST))
async def start_admin(call: CallbackQuery):

    await call.message.edit_text(
        text="Вам разрешен доступ в админ-панель. Выберите необходимое действие.",
        reply_markup=admin_kb()
    )


@router.callback_query(F.data == 'statistics', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_stats(call: CallbackQuery):
    # сделать в сервисах пользователя и сервера функции для статистики
    # клавиатура для подбора статистики

    stats = get_inbounds()
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


@router.callback_query(F.data == 'handler_key', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_user(call: CallbackQuery):
    await call.message.edit_text(
        text="Choose option",
        reply_markup=admin_kb_key()
    )


@router.callback_query(F.data == 'get_all_keys', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_get_all_keys(call: CallbackQuery):
    data = get_inbounds()

    inbounds = data.get('obj')
    for client in inbounds[0].get('clientStats'):
        stats = (
            f"<b>ID ключа:</b> <code>{client.get('id')}</code>\n"
            f"<b>Статус ключа:</b> {'✅ Активен' if client.get('enable') else '❌ Отключен'}\n"
            f"<b>Email пользователя:</b> <code>{client.get('email')}</code>\n"
            f"<b>Остаток жизни:</b> <code>{client.get('expiryTime')}</code>\n"
            f"Total GB <code>{client.get('total')}</code>\n"
        )
        await call.message.edit_text(
            text=stats,
            reply_markup=admin_kb_current_key()
        )


@router.callback_query(F.data == 'generate_key', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_generate_key(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(text=f"Для генерации ключа введите email (название):\n 0 для случайного имени", reply_markup=admin_cancel_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.email)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.email)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await del_msg(message, state)

    msg = await message.edit_text(text=f"Введите число для ограничения IP\n 0 - безлимитное число пользователей", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.limit_ip)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.limitIp)
async def admin_get_total(message: Message, state: FSMContext):
    await state.update_data(limit_ip=message.text)
    await del_msg(message, state)

    msg = await message.edit_text(text=f"Введите число для ограничения объема трафика\n 0 - безлимитный объем трафика", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.total_gb)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.totalGB)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(total_gb=message.text)
    await del_msg(message, state)

    msg = await message.edit_text(text=f"Введите дату действия ключа\n 0 - неограниченное время пользования", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.expire_time)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.expiryTime)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(expire_time=message.text)
    await del_msg(message, state)

    data = await state.get_data()
    text = (
        f"Проверьте введенные поля\n"
        f"Имя ключа {data['email']}\n"
        f"Число устройств {data['limit_ip']}\n"
        f"Лимит трафика {data['total_gb']}\n"
        f"Время действия {data['expire_time']}\n"
    )
    msg = await message.edit_text(text=text, reply_markup=admin_kb_confirm_add())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.confirm)


@router.callback_query(F.data == 'confirm_add', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_confirm_add(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data["last_msg_id"])
    del data["last_msg_id"]
    # make in key service generating key
    key = add_client(data)


@router.callback_query(F.data == 'upd_balance_user', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_update_balance(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(text="input telegram id", reply_markup=admin_cancel_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(UpdateBalance.telegram_id)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), UpdateBalance.telegram_id)
async def admin_get_tg_id(message: Message, state: FSMContext):
    try:
        telegram_id = message.text
        await state.update_data(telegram_id=telegram_id)
        await del_msg(message, state)
        msg = await message.edit_text(text="Enter updated balance", reply_markup=admin_cancel_kb())
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(UpdateBalance.balance)
    except ValueError:
        await message.edit_text(text="Error. Input number (user ID)")
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
        msg = await message.edit_text(text=text, reply_markup=admin_kb_confirm_upd())
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(UpdateBalance.confirm)
    except ValueError:
        await message.edit_text(text="Error. Enter valid balance")
        return


@router.callback_query(F.data == 'confirm_add', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_confirm_update(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    del data['last_msg_id']
    # User service update balance
    await call.message.edit_text(text="Updated successfully", reply_markup=admin_kb())


@router.callback_query(F.data == 'add_key_user', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_add_key_user(call: CallbackQuery, state: FSMContext):
    pass