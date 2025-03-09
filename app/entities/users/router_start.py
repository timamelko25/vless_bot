import asyncio
from datetime import datetime

from loguru import logger
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from app.config import bot, settings
from app.utils.utils import del_msg
from app.entities.servers.service import ServerService
from app.entities.keys.service import KeyService
from .schemas import NewUserScheme
from .service import UserService
from .kb import main_inline_kb, profile_inline_kb, keys_inline_kb


router = Router()


async def HOME_TEXT() -> str:
    return (
        f"<b>🌐 VPN bot на протоколе VLESS</b>\n\n"
        f"⚡ <i>Быстрый</i>, <i>надёжный</i>\n"
        f"🎁 <b>3 дня бесплатно</b>, до 3 устройств на 1 ключ\n"
        f"💸 <b>150 рублей</b> за 1 ключ\n"
        f"💎 Есть <b>реферальная система</b>\n\n"
        f"<b>🚀 Почему выбирают нас:</b>\n"
        f"1️⃣ Высокая скорость соединения\n"
        f"2️⃣ Легкость в подключении и настройке\n"
        f"3️⃣ Полная анонимность и безопасность данных\n\n"
        f"<i>🔥 Подключайся и получай максимум от интернета!</i>\n"
    )


async def PROFILE_TEXT(balance: float, date_expire: datetime | None, refer_id: str) -> str:
    return (
        f" <b>💼 Личный кабинет</b>\n\n"
        f" <b>💰 Баланс:</b> <i>{balance}</i>\n"
        f" <b>📅 Ближайшая дата списания:</b> <i>{date_expire}</i>\n"
        f" <b>🔗 Ваша реферальная ссылка:</b>\n"
        f" <code>https://t.me/vless_tgbot?start={refer_id} </code>\n\n"
        f" ✨ Используйте реферальную систему, чтобы получить бонусы!"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)

    user_info = NewUserScheme(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        refer_id=command.args
    )

    user = await UserService.find_one_or_none(telegram_id=user_info.telegram_id)

    if user is None:
        await UserService.add(
            **user_info.model_dump()
        )

        if user_info.refer_id:
            await UserService.update_count_refer(telegram_id=user_info.refer_id)
            logger.info(
                f"New user reg with ref system {user_info.model_dump()}")
        else:
            logger.info(f"New user reg {user_info.model_dump()}")

    await message.answer(
        text=await HOME_TEXT(),
        reply_markup=main_inline_kb(message.from_user.id)
    )


@router.message(Command('profile'))
async def profile_command(message: Message, state: FSMContext):
    await state.clear()

    user = await UserService.find_one_or_none(telegram_id=str(message.from_user.id))

    if user is not None:
        await message.answer(
            text=await PROFILE_TEXT(user.balance, None, str(message.from_user.id)),
            reply_markup=profile_inline_kb()
        )


@router.callback_query(F.data == 'home')
async def page_home(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        text=await HOME_TEXT(),
        reply_markup=main_inline_kb(call.from_user.id)
    )


@router.callback_query(F.data == 'get_profile')
async def get_user_profile(call: CallbackQuery):

    user = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))

    if user is not None:
        await call.message.edit_text(
            text=await PROFILE_TEXT(user.balance, None, str(call.from_user.id)),
            reply_markup=profile_inline_kb()
        )


@router.callback_query(F.data == 'get_help')
async def get_help_for_key(call: CallbackQuery):

    await call.message.edit_text(
        text=(
            f"Инструкции для установки ключей"
        ),
        reply_markup=keys_inline_kb()
    )


@router.callback_query(F.data == 'promocode')
async def get_promocode(call: CallbackQuery):
    pass


@router.callback_query(F.data == 'get_all_keys')
async def get_all_user_keys(call: CallbackQuery):
    pass
