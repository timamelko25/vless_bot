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
    servers_kb,
    instructions_kb,
    top_up_kb,
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
                reply_markup=servers_kb(servers_list),
            )
        else:
            await call.edit_text(
                "<b>🌍 Выберете сервер</b>",
                reply_markup=servers_kb(servers_list),
            )


@router.callback_query(F.data.startswith("get_key_confirm:"))
async def get_key_confirm(call: CallbackQuery, state: FSMContext):
    _, server_name = call.data.split(":", 1)
    await state.update_data(server_name=server_name)

    user = await UserService.find_one_or_none(telegram_id=call.from_user.id)
    text = (
        f"<b>💼 Текущий баланс:</b> <i>{user.balance} ₽</i>\n\n"
        f"<b>Стоимость ключа:</b> <i>150 ₽</i>\n"
        f"<b>Страна подключения:</b> <i>{server_name}</i>\n\n"
        f"Один ключ поддерживает до <b>3 устройств</b>\n"
        f"Лимит трафика: <b>100 ГБ</b> на ключ\n"
    )

    await call.message.edit_text(
        text=text,
        reply_markup=kb_confirm_get_key(user.balance),
    )


@router.callback_query(F.data == "get_key")
async def get_key(call: CallbackQuery, state: FSMContext):
    user = await UserService.find_one_or_none(telegram_id=call.from_user.id)

    data = await state.get_data()
    server_name = data.get("server_name")

    if user.balance >= 150.0:
        await call.message.edit_text(text="Идет генерация ключа")

        key = await UserService.create_key(
            telegram_id=call.from_user.id, server_name=server_name
        )
        
        if not key:
            await call.message.edit_text(
                text="Ошибка генерации ключа, попробуйте снова",
                reply_markup=kb_confirm_get_key(user.balance),
            )
        logger.info(f"User {user.telegram_id} bought key {key.get('email')}")

        date = int(key.get("expires_at"))
        date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).strftime("%Y-%m-%d")

        text = (
            "🎉Вы приобрели ключ!\n\n"
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
            reply_markup=instructions_kb(),
        )
    else:
        text = (
            "❌ <b>Недостаточно средств!</b>\n\n"
            f"<b>Текущий баланс:</b> <i>{user.balance} ₽</i>\n"
            f"<b>Цена ключа:</b> <b>150 рублей</b> за 1 шт.\n\n"
            "<b>Пополните баланс</b>, чтобы получить ключ."
        )

        await call.message.edit_text(
            text=text,
            reply_markup=top_up_kb(),
        )
