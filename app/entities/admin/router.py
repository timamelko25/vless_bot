from datetime import datetime, timezone
import uuid

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
from app.entities.promocodes.service import PromocodeService
from .kb import admin_kb, admin_kb_confirm_add_key, admin_kb_promo, admin_kb_server, admin_kb_user, admin_kb_key, admin_cancel_kb, admin_kb_current_key, admin_kb_confirm_upd_balance, admin_kb_confirm_add_server, admin_kb_confirm_gen_promo

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
    server = State()
    confirm = State()


class NewServer(StatesGroup):
    name = State()
    domain = State()
    confirm = State()


class NewPromo(StatesGroup):
    code = State()
    count = State()
    bonus = State()
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
    msg = await call.message.edit_text(text=f"Для добавления сервера введите Название\n", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.name)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewServer.name)
async def admin_get_name_server(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await del_msg(message, state)

    msg = await message.answer(text=f"Введите доменное имя сервера\n", reply_markup=admin_cancel_kb())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.domain)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewServer.domain)
async def admin_get_domain_server(message: Message, state: FSMContext):
    await state.update_data(domain=message.text)
    await del_msg(message, state)
    data = await state.get_data()
    text = (
        f"Проверьте введенные данные\n\n"
        f"Имя сервера для бота {data['name']}\n"
        f"Доменное имя сервера{data['domain']}\n"
    )

    msg = await message.answer(
        text=text,
        reply_markup=admin_kb_confirm_add_server()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.confirm)


@router.callback_query(F.data == 'confirm_add_server', F.from_user.id.in_(settings.ADMINS_LIST), NewServer.confirm)
async def admin_confirm_add_server(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    try:
        info = await ServerService.add(
            name=data['name'],
            domain=data['domain']
        )
        if info:
            msg = await call.message.edit_text(
                text="Сервер успешно добавлен",
                reply_markup=admin_kb()
            )
    except Exception as e:
        logger.error(f"Ошибка при добавлении сервера {e}")
        await call.message.edit_text(
            text="Ошибка при добавлении сервера",
            reply_markup=admin_kb()
        )


@router.callback_query(F.data == 'handler_key', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_user(call: CallbackQuery):
    await call.message.edit_text(
        text="Choose option",
        reply_markup=admin_kb_key()
    )


@router.callback_query(F.data == 'get_all_keys_admin', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_get_all_keys(call: CallbackQuery):

    keys = await KeyService.find_all()
    if not keys:
        await call.message.edit_text(
            text="Нет выпущенных ключей",
            reply_markup=admin_kb()
        )
    else:
        await call.message.edit_text(
            text="Все выпущенные ключи"
        )
        for key in keys:
            user = await UserService.find_one_or_none(id=key.user_id)
            server = await ServerService.find_one_or_none(id=key.server_id)
            text = (
                f"<b>ID пользователя:</b> <code>{user.telegram_id}</code>\n"
                f"<b>Сервер ключа:</b> <code>{server.name}</code>\n"
                f"<b>ID ключа:</b> <code>{key.id_panel}</code>\n"
                f"<b>Email пользователя:</b> <code>{key.email}</code>\n"
                f"<b>Остаток жизни:</b> <code>{key.expires_at}</code>\n"
                f"Значение ключа {key.value}"
                f"<b>Статус ключа:</b> {'✅ Активен' if key.get('status') else '❌ Отключен'}\n"
            )
            await call.message.edit_text(
                text=text,
                reply_markup=admin_kb_key() # сделать нормальную клаву для обновления ключа удаления или что-то еще (посмотреть из бота самой панели)
                )


@router.callback_query(F.data == 'generate_key_admin', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_generate_key(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(
        text=f"Для генерации ключа введите telegram_id для присвоения:\n 0 для генерации на админа",
        reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.telegram_id)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.telegram_id)
async def admin_get_telegram_id(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.text)
    await del_msg(message, state)

    msg = await message.answer(
        text=f"Для генерации ключа введите email (название):\n 0 для случайного имени",
        reply_markup=admin_cancel_kb()
    )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.email)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.email)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await del_msg(message, state)

    msg = await message.answer(
        text=f"Введите число для ограничения IP\n 0 - безлимитное число пользователей",
        reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.limitIp)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.limitIp)
async def admin_get_total(message: Message, state: FSMContext):
    await state.update_data(limitIp=message.text)
    await del_msg(message, state)

    msg = await message.answer(
        text=f"Введите число для ограничения объема трафика в битах\n 0 - безлимитный объем трафика",
        reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.totalGB)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.totalGB)
async def admin_get_server(message: Message, state: FSMContext):
    await state.update_data(totalGB=message.text)
    await del_msg(message, state)
    # сделать reply kb для выбора сервера
    msg = await message.answer(
        text="Введите название сервера",
        reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.server)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.server)
async def admin_get_email(message: Message, state: FSMContext):
    await state.update_data(totalGB=message.text)
    await del_msg(message, state)
    # добавить поиск сервера в бд если нет то ввести еще раз
    msg = await message.answer(
        text=f"Введите дату действия ключа в формате (год-число-месяц)\n 0 - неограниченное время пользования",
        reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.expiryTime)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.expiryTime)
async def admin_get_email(message: Message, state: FSMContext):
    date = message.text
    expiryTime = 0 if date == 0 else date.timestamp() * 1000
    await state.update_data(expiryTime=expiryTime)
    await del_msg(message, state)

    data = await state.get_data()
    email = str(uuid.uuid4()).replace(
        '-', '')[:10] if data['email'] == 0 else data['email']

    text = (
        f"Проверьте введенные поля\n"
        f"ID пользователя {data['telegram_id']}\n"
        f"Имя ключа {email}\n"
        f"Число устройств {data['limitIp']}\n"
        f"Лимит трафика {data['totalGB']}\n"
        f"Время действия {date}\n"
    )
    msg = await message.answer(
        text=text,
        reply_markup=admin_kb_confirm_add_key()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.confirm)


@router.callback_query(F.data == 'confirm_add_key', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_confirm_add_key(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # await bot.delete_message(chat_id=call.from_user.id, message_id=data["last_msg_id"])
    del data["last_msg_id"]

    try:
        info = await KeyService.generate_key(data)
        if info:
            await call.edit_text(
                text="Ключ успешно добавлен",
                reply_markup=admin_kb_confirm_add_key()
            )
    except Exception as e:
        logger.error(f"Ошибка при добавлении ключа из админки {e}")
        await call.edit_text(
            text="Ошибка при добавлении ключа",
            reply_markup=admin_kb_confirm_add_key()
        )


@router.callback_query(F.data == 'upd_balance_user', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_update_balance(call: CallbackQuery, state: FSMContext):

    msg = await call.message.edit_text(text="input telegram id", reply_markup=admin_cancel_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(UpdateBalance.telegram_id)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), UpdateBalance.telegram_id)
async def admin_get_tg_id(message: Message, state: FSMContext):
    await del_msg(message, state)
    try:
        telegram_id = message.text
        await state.update_data(telegram_id=telegram_id)

        user = await UserService.find_one_or_none(telegram_id=str(telegram_id))

        if user:
            msg = await message.answer(text="Enter updated balance", reply_markup=admin_cancel_kb())
            await state.update_data(last_msg_id=msg.message_id)
            await state.set_state(UpdateBalance.balance)
        else:
            msg = await message.answer(text="User not found, enter correct telegram id", reply_markup=admin_cancel_kb())
            await state.update_data(last_msg_id=msg.message_id)
            await state.set_state(UpdateBalance.telegram_id)
        # await del_msg(message, state)

    except ValueError:
        await message.edit_text(text="Error. Input number (user ID)")
        return


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), UpdateBalance.balance)
async def admin_get_balance(message: Message, state: FSMContext):
    await del_msg(message, state)
    try:
        balance = float(message.text)
        await state.update_data(balance=balance)

        data = await state.get_data()

        text = (
            f"Check all fields\n\n"
            f"Telegram ID: {data['telegram_id']}\n"
            f"New balance: {data['balance']}\n"
        )

        msg = await message.answer(
            text=text,
            reply_markup=admin_kb_confirm_upd_balance()
        )
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(UpdateBalance.confirm)
    except ValueError:
        await message.answer(text="Error. Enter valid balance")
        return


@router.callback_query(F.data == 'confirm_upd_balance', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_confirm_update_balance(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    del data['last_msg_id']

    try:
        info = await UserService.update_balance(telegram_id=str(data['telegram_id']), balance=float(data['balance']))
        if info:
            await call.message.answer(text="Updated successfully", reply_markup=admin_kb())
    except Exception as e:
        logger.error(f"Error while updating balance in admin panel {e}")
        await call.message.answer(text="Ошибка при обновлении баланса, попробуйте заново", reply_markup=admin_kb())


@router.callback_query(F.data == 'add_key_user', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_add_key_user(call: CallbackQuery, state: FSMContext):
    pass


@router.callback_query(F.data == 'handler_promo', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_promo(call: CallbackQuery):
    await call.message.edit_text(
        text="Choose option",
        reply_markup=admin_kb_promo()
    )


@router.callback_query(F.data == 'gen_promo', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_gen_promo(call: CallbackQuery, state: FSMContext):

    msg = await call.message.edit_text(
        text="Для генерации промокода введите Код активации",
        reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewPromo.code)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewPromo.code)
async def admin_get_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    await del_msg(message, state)

    msg = await message.answer(
        text=("Введите количество активаций промокода"),
        reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewPromo.count)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewPromo.count)
async def admin_get_amount(message: Message, state: FSMContext):
    await del_msg(message, state)
    try:
        count = int(message.text)
        await state.update_data(count=count)

        msg = await message.answer(
            text="Введите бонус при активации промокода",
            reply_markup=admin_cancel_kb()
        )

        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(NewPromo.bonus)
    except ValueError:
        await message.answer(text="Введите корректное количество активаций")


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewPromo.bonus)
async def admin_get_bonus(message: Message, state: FSMContext):

    try:
        bonus = float(message.text)
        await state.update_data(bonus=bonus)
        await del_msg(message, state)

        data = await state.get_data()

        text = (
            f"Проверьте введенные данные\n\n"
            f"Код для активации {data['code']}\n"
            f"Количество активаций {data['count']}\n"
            f"Бонус при активации {data['bonus']}"
        )

        msg = await message.answer(
            text=text,
            reply_markup=admin_kb_confirm_gen_promo()
        )

        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(NewPromo.confirm)
    except ValueError:
        msg = await message.answer(text="Введите корректное число")


@router.callback_query(F.data == 'confirm_gen_promo', F.from_user.id.in_(settings.ADMINS_LIST), NewPromo.confirm)
async def admin_confirm_get_promo(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    del data['last_msg_id']

    try:
        info = await PromocodeService.generate_promocode(data=data)
        if info:
            await call.message.edit_text(
                text="Промокод успешно добавлен",
                reply_markup=admin_kb()
            )
    except Exception as e:
        logger.error(f"Ошибка при добавлении промокода {e}")
        await call.message.edit_text(
            text="Ошибка при добавлении промокода",
            reply_markup=admin_kb()
        )


@router.callback_query(F.data == 'get_all_promo', F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_get_all_promo(call: CallbackQuery):

    promocodes_info = await PromocodeService.find_all()

    if not promocodes_info:
        await call.message.edit_text(
            text="Нет добавленных промокодов",
            reply_markup=admin_kb_promo()
        )
    else:
        text = (
            f"Все выпущенные промокоды\n\n"
        )
        for promo in promocodes_info:
            text += (
                f"Код активации {promo.code}\n"
                f"Осталось активаций {promo.count}\n"
                f"Бонус пополнения {promo.bonus}\n\n"
            )
        await call.message.edit_text(
            text=text,
            reply_markup=admin_kb_promo()
        )
