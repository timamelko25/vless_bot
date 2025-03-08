from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from loguru import logger

from app.config import bot, settings
from app.utils.utils import del_msg

from datetime import datetime

from .schemas import NewUserScheme
from .service import UserService
from app.entities.servers.service import ServerService
from app.entities.keys.service import KeyService

from .kb import main_inline_kb, profile_inline_kb, servers_inline_kb, keys_inline_kb, kb_confirm_upd, home_inline_kb, get_key_inline_kb

router = Router()


async def HOME_TEXT() -> str:
    return (
        f"<b>🌐 VPN bot на протоколе VLESS</b>\n\n"
        f"⚡ <i>Быстрый</i>, <i>надёжный</i>\n"
        f"🎁 <b>3 дня бесплатно</b>, до 3 устройств на 1 ключ\n"
        f"💸 <b>70 рублей</b> за 1 ключ\n"
        f"💎 Есть <b>реферальная система</b>\n"
        f"<b>🚀 Почему выбирают нас:</b>\n"
        f"1️⃣ Высокая скорость соединения\n"
        f"2️⃣ Легкость в подключении и настройке\n"
        f"3️⃣ Полная анонимность и безопасность данных\n"
        f"<i>🔥 Подключайся и получай максимум от интернета!</i>\n"
    )


async def PROFILE_TEXT(balance: float, date_expire: datetime | None, refer_id: str) -> str:
    return (
        f" <b>💼 Личный кабинет</b>\n\n"
        f" <b>💰 Баланс:</b> <i>{balance}</i>\n"
        f" <b>📅 Ближайшая дата списания:</b> <i>{date_expire}</i>\n"
        f" <b>🔗 Ваша реферальная ссылка:</b>\n"
        f" <code>https://t.me/vless_tgbot?start={refer_id} </code>\n"
        f" ✨ Используйте реферальную систему, чтобы получить бонусы и подарки!"
    )


class AddBalance(StatesGroup):
    balance = State()
    confirm = State()


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
            text=await PROFILE_TEXT(user.balance, None, user.refer_id),
            reply_markup=profile_inline_kb()
        )


@router.callback_query(F.data == 'home')
async def page_home(call: CallbackQuery):

    await call.message.edit_text(
        text=await HOME_TEXT(),
        reply_markup=main_inline_kb(call.from_user.id)
    )


@router.callback_query(F.data == 'get_profile')
async def get_user_profile(call: CallbackQuery):
    # user service find user from_user.id
    user = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))

    if user is not None:
        await call.message.edit_text(
            text=await PROFILE_TEXT(user.balance, None, user.refer_id),
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


@router.callback_query(F.data == 'top_up')
async def update_user_balance(call: CallbackQuery, state: FSMContext):

    msg = await call.message.edit_text(
        f"Введите сумму для пополнения"
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddBalance.balance)


@router.message(F.text, AddBalance.balance)
async def get_balance(message: Message, state: FSMContext):
    try:
        balance = float(message.text.replace(',', '.').strip())
        if balance < 10:
            await message.answer("Ошибка. Минимальная сумма пополнения 10")
            return
        elif balance > 10000:
            await message.answer("Ошибка. Максимальная сумма пополнения 10000!")
            return
        await state.update_data(balance=balance)


        data = await state.get_data()

        text = (
            f"Баланс будет пополнен на:\n"
            f"{data['balance']}"
        )
        msg = await message.answer(text=text, reply_markup=kb_confirm_upd())
        await del_msg(message, state)

        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(AddBalance.confirm)
    except ValueError:
        await message.answer(text="Ошибка. Введите корректный баланс!")
        return


@router.callback_query(F.data == 'confirm_add_balance')
async def confirm_add_balance(call: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    # await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    # del data['last_msg_id']

    user_info = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))
    price = data['balance']
    # добавить нормальную оплату
    # await bot.send_invoice(
    #     chat_id=call.from_user.id,
    #     title=f'Оплата 👉 {price}₽',
    #     description=f'Пожалуйста, завершите оплату в размере {price}₽, чтобы открыть доступ к выбранному товару.',
    #     payload=f"{user_info.id}_{data['balance']}",
    #     provider_token=settings.PROVIDER_TOKEN,
    #     currency='rub',
    #     prices=[LabeledPrice(
    #         label=f'Оплата {price}',
    #         amount=int(price) * 100
    #     )],
    #     reply_markup=home_inline_kb()
    # )

    # await call.message.delete
    invoice = True
    if invoice:
        await UserService.update_balance(
            telegram_id=str(call.from_user.id),
            balance=data['balance']
        )

        await call.message.edit_text(text="Баланс успешно пополнен!", reply_markup=home_inline_kb())


# @router.pre_checkout_query(lambda query: True)
# async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    payment_info = message.successful_payment
    user_id, balance = payment_info.invoice_payload.split('_')
    payment_data = {
        'user_id': str(user_id),
        'payment_id': payment_info.telegram_payment_charge_id,
        'price': payment_info.total_amount / 100,
        'balance': int(balance)
    }

    await UserService.update_balance(
        telegram_id=str(user_id),
        balance=balance
    )

    for admin in settings.ADMINS_LIST:
        try:
            username = message.from_user.username
            user_info = f"@{username} ({message.from_user.id})" if username else f"c ID {message.from_user.id}"

            await bot.send_message(text=(
                f"💲 Пользователь {user_info} пополнил баланс на {balance}"
            ))
        except Exception as e:
            logger.error(
                f"Ошибка при отправке уведомления администраторам: {e}")

    await message.edit_text(text="Баланс успешно пополнен!", reply_markup=home_inline_kb())


@router.callback_query(F.data == 'promocode')
async def get_promocode(call: CallbackQuery):
    pass


@router.callback_query(F.data == 'get_all_keys')
async def get_all_user_keys(call: CallbackQuery):
    pass
