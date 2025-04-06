import uuid
from datetime import timedelta, datetime, timezone

from loguru import logger
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from app.broker.schemas import MessageScheme
from app.config import settings, bot, broker
from app.utils.utils import del_msg
from app.entities.keys.panel_api import get_inbounds
from app.entities.users.service import UserService
from app.entities.keys.service import KeyService
from app.entities.keys.schemas import KeyPayloadScheme
from app.entities.servers.service import ServerService
from app.entities.promocodes.service import PromocodeService
from app.entities.promocodes.schemas import PromocodeScheme

from .kb import (
    admin_kb,
    admin_kb_confirm_add_key,
    admin_kb_confirm_spam_admins,
    admin_kb_del_server,
    admin_kb_key_options,
    admin_kb_messages,
    admin_kb_promo,
    admin_kb_server,
    admin_kb_user,
    admin_kb_key,
    admin_cancel_kb,
    admin_kb_confirm_upd_balance,
    admin_kb_confirm_add_server,
    admin_kb_confirm_gen_promo,
    admin_servers_inline_kb,
)

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


class SpamMessage(StatesGroup):
    spam_message = State()
    confirm = State()
    telegram_id = State()


@router.callback_query(F.data == "cancel", F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_handler_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text="Cancel operation", reply_markup=admin_kb())


@router.callback_query(
    F.data == "admin_panel", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def start_admin(call: CallbackQuery):
    await call.message.edit_text(
        text="Вам разрешен доступ в админ-панель. Выберите необходимое действие.",
        reply_markup=admin_kb(),
    )


@router.callback_query(F.data == "statistics", F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_stats(call: CallbackQuery):
    # сделать в сервисах пользователя и сервера функции для статистики
    # клавиатура для подбора статистики

    stats = await get_inbounds()
    await call.message.edit_text(text=stats, reply_markup=admin_kb())


@router.callback_query(
    F.data == "handler_user", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_handler_user(call: CallbackQuery):
    await call.message.edit_text(text="Choose option", reply_markup=admin_kb_user())


@router.callback_query(
    F.data == "handler_server", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_handler_server(call: CallbackQuery):
    await call.message.edit_text(text="Choose option", reply_markup=admin_kb_server())


@router.callback_query(
    F.data == "get_servers_admin", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_del_server(call: CallbackQuery):
    servers = await ServerService.find_all()
    await call.message.delete()
    for server in servers:
        text = (
            f"Имя {server.name}\n"
            f"Домен {server.domain}\n"
            f"Количество купленных ключей {len(server.keys)}"
        )
        await call.message.answer(
            text=text, reply_markup=admin_kb_del_server(server.name)
        )
    await call.message.answer(
        text="Все выделенные сервера", reply_markup=admin_kb_server()
    )


@router.callback_query(F.data.startswith("del_server_admin:"))
async def admin_del_server_confirm(call: CallbackQuery):
    server_name = call.data.split(":")[1]
    await ServerService.delete_server(server_name=server_name)

    await call.message.edit_text(text="Сервер успешно удален")


@router.callback_query(
    F.data == "add_server_admin", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_add_server(call: CallbackQuery, state: FSMContext):
    await state.clear()
    msg = await call.message.edit_text(
        text="Для добавления сервера введите Название\n", reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.name)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewServer.name)
async def admin_get_name_server(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await del_msg(message, state)

    msg = await message.answer(
        text="Введите доменное имя сервера\n", reply_markup=admin_cancel_kb()
    )

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
        f"Доменное имя сервера {data['domain']}\n"
    )

    msg = await message.answer(text=text, reply_markup=admin_kb_confirm_add_server())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewServer.confirm)


@router.callback_query(
    F.data == "confirm_add_server",
    F.from_user.id.in_(settings.ADMINS_LIST),
    NewServer.confirm,
)
async def admin_confirm_add_server(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    try:
        info = await ServerService.add(name=data["name"], domain=data["domain"])
        if info:
            await call.message.edit_text(
                text="Сервер успешно добавлен", reply_markup=admin_kb()
            )
    except Exception as e:
        logger.error(f"Ошибка при добавлении сервера {e}")
        await call.message.edit_text(
            text="Ошибка при добавлении сервера", reply_markup=admin_kb()
        )


@router.callback_query(
    F.data == "handler_key", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_handler_key(call: CallbackQuery):
    await call.message.edit_text(text="Choose option", reply_markup=admin_kb_key())


@router.callback_query(
    F.data == "get_all_keys_admin", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_get_all_keys(call: CallbackQuery):
    keys = await KeyService.find_all()
    if not keys:
        await call.message.edit_text(
            text="Нет выпущенных ключей", reply_markup=admin_kb()
        )
    else:
        for key in keys:
            user = await UserService.find_one_or_none(id=key.user_id)
            server = await ServerService.find_one_or_none(id=key.server_id)
            date = int(key.expires_at)
            date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d"
            )
            text = (
                f"<b>ID пользователя:</b> <code>{user.telegram_id}</code>\n"
                f"<b>Сервер ключа:</b> <code>{server.name}</code>\n"
                f"<b>ID ключа:</b> <code>{key.id_panel}</code>\n"
                f"<b>Email пользователя:</b> <code>{key.email}</code>\n"
                f"<b>Остаток жизни:</b> <code>{date}</code>\n"
                f"Значение ключа {key.value}\n"
                f"<b>Статус ключа:</b> {'✅ Активен' if key.status else '❌ Отключен'}"
            )
            await call.message.answer(
                text=text,
                reply_markup=admin_kb_key_options(
                    key.id
                ),  # сделать нормальную клаву для обновления ключа удаления или что-то еще (посмотреть из бота самой панели)
            )
        await call.message.answer(
            text="Все выпущенные ключи", reply_markup=admin_kb_key()
        )


@router.callback_query(
    F.data.startswith("reset_param:"), F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_reset_key(call: CallbackQuery):
    key_id = call.data.split(":")[1]
    param = call.data.split(":")[2]

    try:
        key = await KeyService.find_one_or_none(id=int(key_id))
        data = KeyPayloadScheme(
            id=key.id_panel,
            email=key.email,
            limitIp=3,
            totalGb=107374182400,
            expiryTime=key.expires_at,
            status=key.status,
        )

        if param == "expiryTime":
            current_time = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            new_time = current_time + timedelta(days=30)
            date = int(new_time.timestamp() * 1000)
            data.expiryTime = date

            await KeyService.update_key(data=data, server=key.server)

            await call.message.edit_text(
                text=f"Ключ (время жизни) {key.email} успешно обновлен",
                reply_markup=admin_kb_key(),
            )
        elif param == "delete":
            await KeyService.delete_key(uuid=key.id_panel, server=key.server)

            await call.message.edit_text(text=f"Ключ {key.email} успешно удален")
    except Exception as e:
        logger.error(f"Error while updating from admin panel {e}")

        await call.message.answer(
            text="Ошибка при действии с ключом", reply_markup=admin_kb_key()
        )


# сделать вывод всех ключей по серверам


@router.callback_query(
    F.data == "generate_key_admin", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_generate_key(call: CallbackQuery, state: FSMContext):
    await state.clear()
    msg = await call.message.edit_text(
        text="Для генерации ключа введите telegram_id для присвоения:\n 0 для генерации на админа",
        reply_markup=admin_cancel_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.telegram_id)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.telegram_id)
async def admin_get_telegram_id(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id) if message.text == "0" else message.text
    await state.update_data(telegram_id=telegram_id)
    await del_msg(message, state)
    # добавить проверку пользователя
    msg = await message.answer(
        text="Для генерации ключа введите email (название):\n 0 для случайного имени",
        reply_markup=admin_cancel_kb(),
    )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.email)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.email)
async def admin_get_email_keygen(message: Message, state: FSMContext):
    email = (
        str(uuid.uuid4()).replace("-", "")[:10] if message.text == "0" else message.text
    )

    await state.update_data(email=email)
    await del_msg(message, state)

    msg = await message.answer(
        text="Введите число для ограничения IP\n 0 - безлимитное число пользователей",
        reply_markup=admin_cancel_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.limitIp)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.limitIp)
async def admin_get_limit(message: Message, state: FSMContext):
    await state.update_data(limitIp=int(message.text))
    await del_msg(message, state)

    msg = await message.answer(
        text="Введите число для ограничения объема трафика в битах\n 0 - безлимитный объем трафика",
        reply_markup=admin_cancel_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.totalGB)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.totalGB)
async def admin_get_totalgb(message: Message, state: FSMContext):
    await state.update_data(totalGB=int(message.text))
    await del_msg(message, state)

    servers = await ServerService.get_servers_list()

    msg = await message.answer(
        text="Введите название сервера", reply_markup=admin_servers_inline_kb(servers)
    )

    await state.update_data(last_msg_id=msg.message_id)


@router.callback_query(
    F.data.startswith("admin_confirm:"), F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_get_server(call: CallbackQuery, state: FSMContext):
    _, server_name = call.data.split(":", 1)
    await state.update_data(server=server_name)

    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data["last_msg_id"])
    msg = await call.message.answer(
        text="Введите дату действия ключа в формате (год-число-месяц)\n 0 - неограниченное время пользования",
        reply_markup=admin_cancel_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.expiryTime)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewKey.expiryTime)
async def admin_get_email(message: Message, state: FSMContext):
    date = message.text

    if date == "0":
        expiryTime = "0"
    else:
        date_obj = datetime.strptime(date, "%Y-%d-%m")
        expiryTime = str(date_obj.timestamp() * 1000)

    await state.update_data(expiryTime=expiryTime)
    await del_msg(message, state)

    data = await state.get_data()

    text = (
        f"Проверьте введенные поля\n"
        f"ID пользователя {data['telegram_id']}\n"
        f"Имя ключа {data['email']}\n"
        f"Сервер {data['server']}\n"
        f"Число устройств {'Безлимит' if data['limitIp'] == 0 else data['limitIp']}\n"
        f"Лимит трафика {'Безлимит' if data['totalGB'] == 0 else data['totalGB']}\n"
        f"Время действия {'Безлимит' if date == '0' else date}\n"
    )
    msg = await message.answer(text=text, reply_markup=admin_kb_confirm_add_key())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewKey.confirm)


@router.callback_query(
    F.data == "confirm_add_key", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_confirm_add_key(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["id"] = str(uuid.uuid4())
    # await bot.delete_message(chat_id=call.from_user.id, message_id=data["last_msg_id"])

    telegram_id = data["telegram_id"]

    del data["last_msg_id"]

    try:
        info = await UserService.create_key(
            telegram_id=telegram_id, server_name=data["server"], data=data
        )
        if info:
            await call.message.edit_text(
                text="Ключ успешно добавлен", reply_markup=admin_kb_key()
            )
    except Exception as e:
        logger.error(f"Ошибка при добавлении ключа из админки {e}")
        await call.message.edit_text(
            text="Ошибка при добавлении ключа", reply_markup=admin_kb_key()
        )


@router.callback_query(
    F.data == "upd_balance_user", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_update_balance(call: CallbackQuery, state: FSMContext):
    await state.clear()
    msg = await call.message.edit_text(
        text="input telegram id", reply_markup=admin_cancel_kb()
    )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(UpdateBalance.telegram_id)


@router.message(
    F.text, F.from_user.id.in_(settings.ADMINS_LIST), UpdateBalance.telegram_id
)
async def admin_get_tg_id(message: Message, state: FSMContext):
    await del_msg(message, state)
    try:
        telegram_id = message.text
        await state.update_data(telegram_id=telegram_id)

        user = await UserService.find_one_or_none(telegram_id=str(telegram_id))

        if user:
            msg = await message.answer(
                text="Enter updated balance", reply_markup=admin_cancel_kb()
            )
            await state.update_data(last_msg_id=msg.message_id)
            await state.set_state(UpdateBalance.balance)
        else:
            msg = await message.answer(
                text="User not found, enter correct telegram id",
                reply_markup=admin_cancel_kb(),
            )
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
            text=text, reply_markup=admin_kb_confirm_upd_balance()
        )
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(UpdateBalance.confirm)
    except ValueError:
        await message.answer(text="Error. Enter valid balance")
        return


@router.callback_query(
    F.data == "confirm_upd_balance", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_confirm_update_balance(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data["last_msg_id"])
    del data["last_msg_id"]

    try:
        info = await UserService.update_balance(
            telegram_id=str(data["telegram_id"]), balance=float(data["balance"])
        )
        if info:
            await call.message.answer(
                text="Updated successfully", reply_markup=admin_kb()
            )
    except Exception as e:
        logger.error(f"Error while updating balance in admin panel {e}")
        await call.message.answer(
            text="Ошибка при обновлении баланса, попробуйте заново",
            reply_markup=admin_kb(),
        )


@router.callback_query(
    F.data == "add_key_user", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_add_key_user(call: CallbackQuery, state: FSMContext):
    pass


@router.callback_query(
    F.data == "handler_promo", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_handler_promo(call: CallbackQuery):
    await call.message.edit_text(text="Choose option", reply_markup=admin_kb_promo())


@router.callback_query(F.data == "gen_promo", F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_gen_promo(call: CallbackQuery, state: FSMContext):
    await state.clear()
    msg = await call.message.edit_text(
        text="Для генерации промокода введите Код активации",
        reply_markup=admin_cancel_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(NewPromo.code)


@router.message(F.text, F.from_user.id.in_(settings.ADMINS_LIST), NewPromo.code)
async def admin_get_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    await del_msg(message, state)

    msg = await message.answer(
        text=("Введите количество активаций промокода"), reply_markup=admin_cancel_kb()
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
            text="Введите бонус при активации промокода", reply_markup=admin_cancel_kb()
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

        msg = await message.answer(text=text, reply_markup=admin_kb_confirm_gen_promo())

        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(NewPromo.confirm)
    except ValueError:
        msg = await message.answer(text="Введите корректное число")


@router.callback_query(
    F.data == "confirm_gen_promo",
    F.from_user.id.in_(settings.ADMINS_LIST),
    NewPromo.confirm,
)
async def admin_confirm_get_promo(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    del data["last_msg_id"]

    payload = PromocodeScheme(
        code=data["code"], count=data["count"], bonus=data["bonus"]
    )

    try:
        info = await PromocodeService.generate_promocode(data=payload)
        if info:
            logger.info("Промокод успешно добавлен")
            await call.message.edit_text(
                text="Промокод успешно добавлен", reply_markup=admin_kb()
            )
    except Exception as e:
        logger.error(f"Ошибка при добавлении промокода {e}")
        await call.message.edit_text(
            text="Ошибка при добавлении промокода", reply_markup=admin_kb()
        )


@router.callback_query(
    F.data == "get_all_promo", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_get_all_promo(call: CallbackQuery):
    promocodes_info = await PromocodeService.find_all()

    if not promocodes_info:
        await call.message.edit_text(
            text="Нет добавленных промокодов", reply_markup=admin_kb_promo()
        )
    else:
        text = "Все выпущенные промокоды\n\n"
        for promo in promocodes_info:
            text += (
                f"Код активации {promo.code}\n"
                f"Осталось активаций {promo.count}\n"
                f"Бонус пополнения {promo.bonus}\n\n"
            )
        await call.message.edit_text(text=text, reply_markup=admin_kb_promo())


@router.callback_query(
    F.data == "admin_spam_messages", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_start_spam(call: CallbackQuery, state: FSMContext):
    await state.clear()

    msg = await call.message.edit_text(
        text="Введите сообщение для рассылки сообщений\n(поддерживается упрощенное html форматирование)",
        reply_markup=admin_cancel_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(SpamMessage.spam_message)


@router.message(
    F.text, F.from_user.id.in_(settings.ADMINS_LIST), SpamMessage.spam_message
)
async def admin_get_message(message: Message, state: FSMContext):
    await state.update_data(spam_message=message.text)
    await del_msg(message, state)

    text = f"Проверьте введенные данные\n\n{message.text}"

    msg = await message.answer(text=text, reply_markup=admin_kb_confirm_spam_admins())

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(SpamMessage.confirm)


@router.callback_query(
    F.data == "confirm_spam",
    F.from_user.id.in_(settings.ADMINS_LIST),
    SpamMessage.confirm,
)
async def admin_confirm_spam_admins(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text="Выберете кому произвести отправку сообщений",
        reply_markup=admin_kb_messages(),
    )


@router.callback_query(F.data == "spam_admins")
async def admin_spam_admins(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        msg = MessageScheme(
            message=data["spam_message"]
        )
        await broker.publish(msg, "admin_msg")
        logger.info("Генерация рассылки сообщений администраторам")
        await call.message.edit_text(
            text="Сообщения успешно разосланы", reply_markup=admin_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка при генерации отправки сообщения администраторам {e}")


@router.callback_query(F.data == "spam_users", F.from_user.id.in_(settings.ADMINS_LIST))
async def admin_spam_users(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        msg = MessageScheme(
            message=data["spam_message"]
        )

        await broker.publish(msg, "users_msg")
        logger.info("Генерация рассылки сообщений пользователям")
        await call.message.edit_text(
            text="Сообщения успешно разосланы", reply_markup=admin_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка при генерации отправки сообщений пользователям {e}")


@router.callback_query(
    F.data == "send_message", F.from_user.id.in_(settings.ADMINS_LIST)
)
async def admin_send_message(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(
        text="Введите ID пользователя", reply_markup=admin_cancel_kb()
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(SpamMessage.telegram_id)


@router.message(
    F.text, F.from_user.id.in_(settings.ADMINS_LIST), SpamMessage.telegram_id
)
async def admin_spam_get_telegram_id(message: Message, state: FSMContext):
    await del_msg(message, state)
    try:
        user_id = message.text
        user = await UserService.find_one_or_none(telegram_id=user_id)
        if user:
            await state.update_data(telegram_id=user_id)

            data = await state.get_data()

            msg = MessageScheme(
                message=data["spam_message"],
                telegram_id=data["telegram_id"],
            )

            await broker.publish(msg, "send_msg")
            logger.info("Генерация отправки сообщения")
        else:
            msg = await message.answer(
                text="Пользователь не найден, введите другой ID",
                reply_markup=admin_cancel_kb(),
            )
    except Exception as e:
        logger.error(f"Ошибка при генерации отправки сообщения пользователю {e}")
