from datetime import datetime, timezone

from loguru import logger
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.utils.utils import del_msg
from app.entities.servers.service import ServerService
from app.entities.keys.service import KeyService
from app.entities.promocodes.service import PromocodeService
from .schemas import NewUserScheme
from .service import UserService
from .kb import (
    cancel_inline_kb,
    del_key_kb,
    main_inline_kb,
    profile_inline_kb,
    keys_inline_kb,
    promocode_inline_kb,
    home_inline_kb,
)


router = Router()


async def HOME_TEXT() -> str:
    return (
        "<b>🌐 VPN bot на протоколе VLESS</b>\n\n"
        "⚡ <i>Быстрый</i>, <i>надёжный</i>\n"
        "🎁 <b>3 дня бесплатно</b>, до 3 устройств на 1 ключ\n"
        "💸 <b>150 рублей</b> за 1 ключ\n"
        "💎 Есть <b>реферальная система</b>\n\n"
        "<b>🚀 Почему выбирают нас:</b>\n"
        "1️⃣ Высокая скорость соединения\n"
        "2️⃣ Легкость в подключении и настройке\n"
        "3️⃣ Полная анонимность и безопасность данных\n\n"
        "<i>🔥 Подключайся и получай максимум от интернета!</i>\n"
    )


async def PROFILE_TEXT(balance: float, date_expire: str, refer_id: str) -> str:
    return (
        f" <b>💼 Личный кабинет</b>\n\n"
        f" <b>💰 Баланс:</b> <i>{balance}</i>\n"
        f" <b>📅 Ближайшая дата списания:</b> <i>{date_expire}</i>\n\n"
        f" <b>🔗 Ваша реферальная ссылка:</b>\n"
        f" <code>https://t.me/vless_tgbot?start={refer_id} </code>\n\n"
        f" ✨ Используйте реферальную систему, чтобы получать <b>20%</b> от пополнений приведенного друга!\n"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    data = await state.get_data()
    if data.get("last_msg_id"):
        await del_msg(message, state)

    await state.clear()
    user_id = str(message.from_user.id)

    user_info = NewUserScheme(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        refer_id=command.args,
    )

    user = await UserService.find_one_or_none(telegram_id=user_info.telegram_id)

    if user is None:
        await UserService.add(**user_info.model_dump())

        if user_info.refer_id:
            await UserService.update_count_refer(telegram_id=user_info.refer_id)
            logger.info(f"New user reg with ref system {user_info.model_dump()}")
        else:
            logger.info(f"New user reg {user_info.model_dump()}")

    msg = await message.answer(
        text=await HOME_TEXT(), reply_markup=main_inline_kb(message.from_user.id)
    )

    await state.update_data(last_msg_id=msg.message_id)


@router.message(Command("profile"))
async def profile_command(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("last_msg_id"):
        await del_msg(message, state)

    await state.clear()
    tg_id = str(message.from_user.id)
    user = await UserService.find_one_or_none(telegram_id=tg_id)
    date = await UserService.find_min_date_expire(telegram_id=tg_id)
    balance = round(user.balance, 2)

    if date is None:
        date = "Нет купленных ключей"

    msg = await message.answer(
        text=await PROFILE_TEXT(balance, date, str(message.from_user.id)),
        reply_markup=profile_inline_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)


@router.callback_query(F.data == "home")
async def page_home(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        text=await HOME_TEXT(), reply_markup=main_inline_kb(call.from_user.id)
    )


@router.callback_query(F.data == "get_profile")
async def get_user_profile(call: CallbackQuery):
    tg_id = str(call.from_user.id)
    user = await UserService.find_one_or_none(telegram_id=tg_id)
    date = await UserService.find_min_date_expire(telegram_id=tg_id)
    balance = round(user.balance, 2)

    if date is None:
        date = "Нет купленных ключей"

    if user is not None:
        await call.message.edit_text(
            text=await PROFILE_TEXT(balance, date, tg_id),
            reply_markup=profile_inline_kb(),
        )


@router.callback_query(F.data == "get_help")
async def get_help_for_key(call: CallbackQuery):
    await call.message.edit_text(
        text=("Инструкции для установки ключей"), reply_markup=keys_inline_kb()
    )


@router.callback_query(F.data == "promocode")
async def start_promocode(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        text="Введите промокод для активации", reply_markup=cancel_inline_kb()
    )
    await state.update_data(last_msg_id=call.message.message_id)
    await state.set_state()


@router.message(F.text, StateFilter(None))
async def get_promocode(message: Message, state: FSMContext):
    promocode = message.text

    await del_msg(message, state)

    promocode_info = await PromocodeService.find_one_or_none(code=promocode)
    if promocode_info:
        apply_info = await UserService.get_promocode(
            telegram_id=str(message.from_user.id), code=promocode_info.code
        )
        
    if apply_info == False:
        text = "Промокод уже был активирован :(\nПопробуйте ввести другой для активации"
        msg = await message.answer(text=text, reply_markup=promocode_inline_kb())

    if promocode_info and apply_info:
        text = (
            f"Промокод успешно применен!\n"
            f"Ваш баланс пополнен на {promocode_info.bonus}₽"
        )
        msg = await message.answer(text=text, reply_markup=home_inline_kb())
    else:
        text = "Промокод не найден :(\nПопробуйте ввести другой для активации"
        msg = await message.answer(text=text, reply_markup=promocode_inline_kb())

    await state.update_data(last_msg_id=msg.message_id)


@router.callback_query(F.data == "get_all_keys")
async def get_all_user_keys(call: CallbackQuery):
    user_keys = await UserService.get_all_keys(telegram_id=str(call.from_user.id))
    await call.message.delete()
    if user_keys:
        text = "Все ваши купленные ключи\n\n"

        for key in user_keys:
            server = await ServerService.find_one_or_none(id=key.server_id)
            date = int(key.expires_at)
            date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d"
            )
            text = (
                f"Время действия ключа <code>{date}</code>\n"
                f"Страна действия: <b>{server.name}</b>\n"
                f"Статус ключа {'✅ Активен' if key.status else '❌ Отключен'}\n"
                f"Ваш ключ: (нажать на ключ для копирования)\n"
                f"<code>{key.value}</code>\n\n"
            )
            await call.message.answer(
                text=text, reply_markup=del_key_kb(key.email, server.name)
            )

        text = "📜 Для активации воспользуйтесь прикрепленной инструкцией."

        await call.message.answer(text=text, reply_markup=keys_inline_kb())
    else:
        await call.message.answer(
            text="Нет купленных ключей", reply_markup=home_inline_kb()
        )


@router.callback_query(F.data.startswith("confirm_del:"))
async def confirm_delete_key(call: CallbackQuery):
    key_email = call.data.split(":")[1]
    server_name = call.data.split(":")[2]

    key = await KeyService.find_one_or_none(email=key_email)    
    server = await ServerService.find_one_or_none(name=server_name)

    await KeyService.delete_key(uuid=key.id_panel, server=server)

    await call.message.edit_text(text="Ключ успешно удален")
