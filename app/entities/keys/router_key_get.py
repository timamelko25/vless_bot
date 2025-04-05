from datetime import datetime, timezone

from loguru import logger
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.broker.schemas import MessageScheme
from app.config import broker
from app.entities.servers.service import ServerService
from app.entities.users.service import UserService
from app.entities.users.kb import (
    servers_inline_kb,
    keys_inline_kb,
    get_key_inline_kb,
    kb_confirm_get_key,
)

router = Router()


@router.callback_query(F.data == "start_getting_key")
async def get_servers(call: CallbackQuery | Message):
    servers_list = await ServerService.get_servers_list()

    if servers_list:
        if isinstance(call, CallbackQuery):
            await call.message.edit_text(
                "<b>🌍 Выберете сервер</b>",
                reply_markup=servers_inline_kb(servers_list),
            )
        else:
            await call.edit_text(
                "<b>🌍 Выберете сервер</b>",
                reply_markup=servers_inline_kb(servers_list),
            )


@router.callback_query(F.data.startswith("get_key_confirm:"))
async def get_key_confirm(call: CallbackQuery, state: FSMContext):
    _, server_name = call.data.split(":", 1)
    await state.update_data(server_name=server_name)

    user = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))
    text = (
        f"Текущий баланс {user.balance}\n\n"
        f"Для покупки ключа необходимо 150 ₽\n\n"
        f"Ключ будет куплен для страны {server_name}\n"
        f"До 3 устройств на 1 ключ\n"
        f"Лимит трафика на 1 ключ 100 Gb\n"
    )

    await call.message.edit_text(
        text=text, reply_markup=kb_confirm_get_key(user.balance)
    )


@router.callback_query(F.data == "get_key")
async def get_key(call: CallbackQuery, state: FSMContext):
    user = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))
    data = await state.get_data()
    server_name = data.get("server_name")

    if user.balance >= 150.0:
        key = await UserService.create_key(
            telegram_id=str(call.from_user.id), server_name=server_name
        )

        logger.info(f"User {user.telegram_id} bought key {key.get('email')}")

        date = int(key.get("expires_at"))
        date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).strftime("%Y-%m-%d")

        text = (
            "🎉 <b>Поздравляю!</b> Вы приобрели ключ!\n\n"
            f"🌍 <b>Страна покупки:</b> <code>{server_name}</code>\n"
            f"📅 <b>Срок действия:</b> <code>{date}</code>\n\n"
            "🔑 <b>Ваш ключ:</b>\n"
            f"<code>{key.get('value')}</code>\n\n"
            "📜 Для активации воспользуйтесь прикрепленной инструкцией."
        )

        msg = MessageScheme(
            message=f"Пользователь {user.telegram_id} купил ключ {key.get('email')}",
        )

        await broker.publish(
            msg,
            "admin_msg",
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
