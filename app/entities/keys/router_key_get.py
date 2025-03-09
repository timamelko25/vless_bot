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
from app.entities.users.service import UserService
from app.entities.users.kb import servers_inline_kb, keys_inline_kb, get_key_inline_kb
from .service import KeyService

router = Router()


@router.callback_query(F.data == 'start_getting_key')
async def get_servers(call: CallbackQuery):
    servers_list = await ServerService.get_servers_list()
    if servers_list:
        await call.message.edit_text(
            f"<b>🌍 Выберете сервер</b>",
            reply_markup=servers_inline_kb(servers_list)
        )
    else:
        await call.message.edit_text(
            f"<b>🌍 Выберете сервер</b>",
            reply_markup=servers_inline_kb(['Netherlands'])
        )


@router.callback_query(F.data == 'get_key')
async def get_key(call: CallbackQuery):
    user = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))
    server = call.data.split(':')[0]

    if user.balance > 150:
        key = await UserService.create_key(telegram_id=str(call.from_user.id), server=server)

        logger.info(f"User {user.telegram_id} bought key {key.get('email')}")

        text = (
            "🎉 <b>Поздравляю!</b> Вы приобрели ключ!\n\n"
            f"🌍 <b>Страна покупки:</b> <code>{server}</code>\n"
            f"📅 <b>Срок действия:</b> <code>{key.get('expiryTime')}</code>\n\n"
            "🔑 <b>Ваш ключ:</b>\n"
            f"<code>{key.get('value')}</code>\n\n"
            "📜 Для активации воспользуйтесь прикрепленной инструкцией."
        )

        await call.message.edit_text(
            text=text,
            reply_markup=keys_inline_kb(),
        )
    else:
        text = (
            f"❌ <b>Недостаточно средств!</b>\n\n"
            f"Текущий баланс {user.balance}\n"
            f"Цена ключа <b>150 рублей</b> за 1 шт.\n"
            f"💰 Сперва пополните баланс, чтобы получить ключ."
        )

        await call.message.edit_text(
            text=text,
            reply_markup=get_key_inline_kb(),
        )
