from datetime import datetime, timezone
from loguru import logger
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from app.config import settings, bot
from app.utils.utils import del_msg
from app.entities.keys.panel_api import add_client, get_inbounds
from app.entities.users.service import UserService
from app.entities.keys.service import KeyService
from app.entities.servers.service import ServerService
from .kb import admin_kb, admin_kb_confirm_add_key, admin_kb_server, admin_kb_user, admin_kb_key, admin_cancel_kb, admin_kb_current_key, admin_kb_confirm_upd_balance, admin_kb_confirm_add_server

router = Router()


class UpdateBalance(StatesGroup):
    telegram_id = State()
    balance = State()
    confirm = State()


class NewKey(StatesGroup):
    email = State()
    telegram_id = State()
    limitIp = State()
    totalGB = State()
    expiryTime = State()
    confirm = State()


class NewServer(StatesGroup):
    name = State()
    domain = State()
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


@router.callback_query(F.data == 'add_server_admin', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_add_server(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(text=f"Для добавления сервера введите его имя для бота\n", reply_markup=admin_cancel_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.name)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewServer.name)
async def admin_get_name_server(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    # await del_msg(message, state)

    msg = await message.edit_text(text=f"Введите доменное имя сервера\n", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.domain)
    
    
@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewServer.domain)
async def admin_get_domain_server(message: Message, state: FSMContext):
    await state.update_data(domain=message.text)
    # await del_msg(message, state)
    data = await state.get_data()
    text = (
        f"Проверьте введенные данные\n\n"
        f"Имя сервера для бота {data['name']}\n"
        f"Доменное имя сервера{data['domain']}\n"
        )
    
    msg = await message.edit_text(text=text, reply_markup=admin_kb_confirm_add_server())
    
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.confirm)
    
@router.callback_query(F.data == 'confirm_add_server', F.from_user.id.in_(settings.ADMINS_LIST), NewServer.confirm)
async def admin_confirm_add_server(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    info = await ServerService.add(
        name=data['name'],
        # domain=data['domain']
        )
    if info:
        msg = await call.message.answer(text=f"Сервер успешно добавлен", reply_markup=admin_kb())
    else:
        msg = await call.message.answer(text=f"Ошибка при добавлении сервера", reply_markup=admin_kb())

@router.callback_query(F.data == 'handler_key', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_user(call: CallbackQuery):
    await call.message.edit_text(
        text="Choose option",
        reply_markup=admin_kb_key()
    )



@router.callback_query(F.data == 'get_all_keys_admin', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_get_all_keys(call: CallbackQuery):
    data = await get_inbounds()

    inbounds = data.get('obj')
    for client in inbounds[0].get('clientStats'):
        text = (
            f"<b>ID ключа:</b> <code>{client.get('id')}</code>\n"
            f"<b>Статус ключа:</b> {'✅ Активен' if client.get('enable') else '❌ Отключен'}\n"
            f"<b>Email пользователя:</b> <code>{client.get('email')}</code>\n"
            f"<b>Остаток жизни:</b> <code>{client.get('expiryTime')}</code>\n"
            f"Total GB <code>{client.get('total')}</code>\n"
        )
        await call.message.answer(
            text=text,
            reply_markup=admin_kb_current_key()
        )


@router.callback_query(F.data == 'generate_key_admin', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_generate_key(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(text=f"Для генерации ключа введите telegram_id для присвоения:\n 0 для генерации на себя", reply_markup=admin_cancel_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.telegram_id)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.telegram_id)
async def admin_get_telegram_id(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.text)
    # await del_msg(message, state)

    msg = await message.edit_text(text=f"Для генерации ключа введите email (название):\n 0 для случайного имени", reply_markup=admin_cancel_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.email)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.email)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    # await del_msg(message, state)

    msg = await message.edit_text(text=f"Введите число для ограничения IP\n 0 - безлимитное число пользователей", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.limit_ip)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.limitIp)
async def admin_get_total(message: Message, state: FSMContext):
    await state.update_data(limit_ip=message.text)
    # await del_msg(message, state)

    msg = await message.edit_text(text=f"Введите число для ограничения объема трафика в битах\n 0 - безлимитный объем трафика", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.total_gb)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.totalGB)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(total_gb=message.text)
    # await del_msg(message, state)

    msg = await message.edit_text(text=f"Введите дату действия ключа в формате (год-число-месяц)\n 0 - неограниченное время пользования", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.expire_time)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.expiryTime)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(expire_time=message.text)
    # await del_msg(message, state)

    data = await state.get_data()
    date = int(data['expire_time'])
    date = int(date.timestamp() * 1000)
    text = (
        f"Проверьте введенные поля\n"
        f"ID пользователя {data['telegram_id']}\n"
        f"Имя ключа {data['email']}\n"
        f"Число устройств {data['limit_ip']}\n"
        f"Лимит трафика {data['total_gb']}\n"
        f"Время действия {data['expire_time']}\n"
    )
    msg = await message.edit_text(text=text, reply_markup=admin_kb_confirm_add_key())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.confirm)


@router.callback_query(F.data == 'confirm_add_key', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_confirm_add_key(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data["last_msg_id"])
    # del data["last_msg_id"]
    info = await KeyService.generate_key(data)
    if info:
        msg = await call.answer(text=(f"Ключ успешно добавлен"), reply_markup=admin_kb_confirm_add_key())
    else:
        msg = await call.answer(text=(f"Ошибка при добавлении ключа"), reply_markup=admin_kb_confirm_add_key())


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

        user = await UserService.find_one_or_none(telegram_id=str(telegram_id))

        if user:
            msg = await message.edit_text(text="Enter updated balance", reply_markup=admin_cancel_kb())
            await state.update_data(last_msg_id=msg.message_id)
            await state.set_state(UpdateBalance.balance)
        else:
            msg = await message.edit_text(text="User not found, enter correct telegram id", reply_markup=admin_cancel_kb())
            await state.update_data(last_msg_id=msg.message_id)
            await state.set_state(UpdateBalance.telegram_id)
        # await del_msg(message, state)

    except ValueError:
        await message.edit_text(text="Error. Input number (user ID)")
        return


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), UpdateBalance.balance)
async def admin_get_balance(message: Message, state: FSMContext):
    try:
        balance = float(message.text)
        await state.update_data(balance=balance)
        # await del_msg(message, state)

        data = await state.get_data()

        text = (
            f"Check all fields\n\n"
            f"Telegram ID: {data['telegram_id']}\n"
            f"New balance: {data['balance']}\n"
        )

        msg = await message.edit_text(
            text=text,
            reply_markup=admin_kb_confirm_upd_balance()
        )
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(UpdateBalance.confirm)
    except ValueError:
        await message.edit_text(text="Error. Enter valid balance")
        return


@router.callback_query(F.data == 'confirm_upd_balance', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_confirm_update_balance(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    del data['last_msg_id']

    try:
        info = await UserService.update_balance(telegram_id=str(data['telegram_id']), balance=float(data['balance']))
        if info:
            await call.message.edit_text(text="Updated successfully", reply_markup=admin_kb())
    except Exception as e:
        logger.error(f"Error while updating balance in admin panel {e}")
        await call.message.edit_text(text="Ошибка при обновлении баланса, попробуйте заново", reply_markup=admin_kb())


@router.callback_query(F.data == 'add_key_user', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_add_key_user(call: CallbackQuery, state: FSMContext):
    pass
