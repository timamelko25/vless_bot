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
    cancel_kb,
    del_key_kb,
    main_kb,
    profile_kb,
    instructions_kb,
    promocode_kb,
    home_kb,
)


router = Router()


def HOME_TEXT() -> str:
    return (
        "<b>VPN-бот на протоколе VLESS</b>\n\n"
        "<b>Преимущества:</b>\n"
        "• <i>Надёжное и стабильное соединение</i>\n"
        "• <i>Быстрая настройка и подключение</i>\n"
        "• <i>Гарантированная конфиденциальность</i>\n\n"
        "<b>Условия:</b>\n"
        "• <b>3 дня бесплатно</b> — до 3 устройств на один ключ\n"
        "• <b>Стоимость:</b> 150 ₽ за ключ\n"
        "• <b>Реферальная программа</b> — получайте бонусы"
    )


def PROFILE_TEXT(balance: float, date_expire: str, refer_id: int) -> str:
    return (
        f"<b>💼 Личный кабинет</b>\n\n"
        f"<b>Баланс:</b> <i>{balance}</i>\n"
        f"<b>Дата следующего списания:</b> <i>{date_expire}</i>\n\n"
        f"<b>Ваша реферальная ссылка:</b>\n"
        f"<code>https://t.me/vless_tgbot?start={refer_id}</code>\n\n"
        f"<b>Реферальная программа:</b>\n"
        f"Получайте <b>20%</b> от пополнений пользователей, зарегистрированных по вашей ссылке.\n"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    try:
        data = await state.get_data()
        if data.get("last_msg_id", ""):
            await del_msg(message, state)

        await state.clear()
        user_id = message.from_user.id

        user_info = NewUserScheme(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            refer_id=int(command.args) if command.args else None,
        )

        user = await UserService.find_one_or_none(telegram_id=user_info.telegram_id)

        if user is None:
            await UserService.add(**user_info.model_dump())

            if user_info.refer_id:
                await UserService.update_count_refer(telegram_id=user_info.refer_id)
                logger.success(f"New user reg with ref system {user_info.model_dump()}")
            else:
                logger.success(f"New user reg {user_info.model_dump()}")

        msg = await message.answer(
            text=HOME_TEXT(),
            reply_markup=main_kb(user_id),
        )

        await state.update_data(last_msg_id=msg.message_id)
    except ValueError:
        await message.answer("Неправильная ссылка для перехода")


@router.message(Command("profile"))
async def profile_command(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("last_msg_id"):
        await del_msg(message, state)

    await state.clear()
    tg_id = message.from_user.id

    user = await UserService.find_one_or_none(telegram_id=tg_id)
    if user is None:
        user_info = NewUserScheme(
            telegram_id=tg_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            refer_id=None,
        )
        await UserService.add(**user_info.model_dump())
        logger.success(f"New user reg {user_info.model_dump()}")

    date = await UserService.find_min_date_expire(telegram_id=tg_id)

    if date is None:
        date = "Нет купленных ключей"

    msg = await message.answer(
        text=PROFILE_TEXT(round(user.balance, 2), date, tg_id),
        reply_markup=profile_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)


@router.callback_query(F.data == "home")
async def page_home(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        text=HOME_TEXT(),
        reply_markup=main_kb(call.from_user.id),
    )


@router.callback_query(F.data == "get_profile")
async def get_user_profile(call: CallbackQuery):
    logger.info("here")
    tg_id = call.from_user.id
    user = await UserService.find_one_or_none(telegram_id=tg_id)
    date = await UserService.find_min_date_expire(telegram_id=tg_id)

    if date is None:
        date = "Нет купленных ключей"

    if user is not None:
        await call.message.edit_text(
            text=PROFILE_TEXT(round(user.balance, 2), date, tg_id),
            reply_markup=profile_kb(),
        )


@router.callback_query(F.data == "get_help")
async def get_help_for_key(call: CallbackQuery):
    await call.message.edit_text(
        text=("Инструкции для установки ключей"),
        reply_markup=instructions_kb(),
    )


@router.callback_query(F.data == "FAQ")
async def faq(call: CallbackQuery):
    text = (
        "<b>❓ Часто задаваемые вопросы (FAQ)</b>\n\n"
        "<b>🔒 Насколько безопасен протокол VLESS?</b>\n"
        "Протокол VLESS шифрует весь интернет-трафик и исключает утечки данных. "
        "Никакая информация о вашем трафике не сохраняется — мы не ведем логи.\n\n"
        "<b>💳 Как осуществляется оплата?</b>\n"
        "Оплата проходит через безопасный сервис <b>ЮKassa</b>. "
        "Все платежные данные защищены шифрованием Telegram и не сохраняются на стороне бота.\n\n"
        "<b>📆 Как работает система списания?</b>\n"
        "Списание происходит <b>каждые 30 дней</b> автоматически после активации ключа. "
        "Вы всегда можете следить за датой следующего списания в личном кабинете бота.\n\n"
        "<i>Если у вас остались вопросы — напишите администратору для получения ответов.</i>"
    )

    await call.message.edit_text(
        text=text,
        reply_markup=home_kb(),
    )


@router.callback_query(F.data == "promocode")
async def start_promocode(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        text="Введите промокод для активации",
        reply_markup=cancel_kb(),
    )
    await state.update_data(last_msg_id=call.message.message_id)
    await state.set_state("promo")


@router.message(F.text, StateFilter("promo"))
async def get_promocode(message: Message, state: FSMContext):
    promocode = message.text

    await del_msg(message, state)

    promocode_info = await PromocodeService.find_one_or_none(code=promocode)

    if promocode_info:
        apply_info = await UserService.get_promocode(
            telegram_id=message.from_user.id,
            code=promocode_info.code,
        )

        if not apply_info:
            text = (
                "Промокод уже был активирован\nПопробуйте ввести другой для активации"
            )
            msg = await message.answer(
                text=text,
                reply_markup=promocode_kb(),
            )

        elif promocode_info and apply_info:
            text = (
                f"Промокод успешно применен!\n"
                f"Ваш баланс пополнен на {promocode_info.bonus}₽"
            )
            msg = await message.answer(
                text=text,
                reply_markup=home_kb(),
            )
    else:
        text = "Промокод не найден\nПопробуйте ввести другой для активации"
        msg = await message.answer(
            text=text,
            reply_markup=promocode_kb(),
        )

    await state.update_data(last_msg_id=msg.message_id)


@router.callback_query(F.data == "get_all_keys")
async def get_all_user_keys(call: CallbackQuery):
    user_keys = await UserService.get_all_keys(telegram_id=call.from_user.id)

    await call.message.delete()

    if user_keys:
        text = "Все ваши купленные ключи\n\n"

        for key in user_keys:
            date = int(key.expires_at)
            date = datetime.fromtimestamp(date / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d"
            )
            text = (
                f"Время действия ключа <code>{date}</code>\n"
                f"Страна действия: <b>{key.server.name}</b>\n"
                f"Статус ключа {'✅ Активен' if key.status else '❌ Отключен'}\n"
                f"Ваш ключ: (нажать на ключ для копирования)\n"
                f"<code>{key.value}</code>\n\n"
            )
            await call.message.answer(
                text=text,
                reply_markup=del_key_kb(key.email, key.server.name),
            )

        text = "📜 Для активации воспользуйтесь прикрепленной инструкцией."

        await call.message.answer(
            text=text,
            reply_markup=instructions_kb(),
        )
    else:
        await call.message.answer(
            text="Нет купленных ключей",
            reply_markup=home_kb(),
        )


@router.callback_query(F.data.startswith("confirm_del:"))
async def confirm_delete_key(call: CallbackQuery):
    key_email = call.data.split(":")[1]
    server_name = call.data.split(":")[2]

    key = await KeyService.find_one_or_none(email=key_email)
    server = await ServerService.find_one_or_none(name=server_name)

    await KeyService.delete_key(uuid=key.id_panel, server=server)

    await call.message.edit_text(text="Ключ успешно удален")
