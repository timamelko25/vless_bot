from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from loguru import logger

from app.config import bot, settings
from app.utils.utils import del_msg

from .schemas import NewUserScheme
from .service import UserService

from .kb import main_inline_kb, profile_inline_kb, servers_inline_kb, prices_reply_kb, kb_confirm_upd, home_inline_kb

router = Router()


class AddBalance(StatesGroup):
    balance = State()
    confirm = State()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    user_info = NewUserScheme(
        telegram_id=str(user_id),
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
            UserService.update_count_refer(telegram_id=user_id)
            logger.info(f"New user reg with ref system {user_info.model_dump()} with ref")
        else:
            logger.info(f"New user reg {user_info.model_dump()} with ref")

    command_args: str = command.args

    if command_args:
        await message.answer(
            f"<b>🌐 VPN bot на протоколе VLESS</b>\n"
            f"⚡ <i>Быстрый</i>, <i>надёжный</i>\n"
            f"🎁 <b>3 дня бесплатно</b>, до 3 устройств на 1 ключ\n"
            f"💸 <b>70 рублей</b> за 1 ключ\n"
            f"💎 Есть <b>реферальная система</b>\n"
            f"<b>🚀 Почему выбирают нас:</b>\n"
            f"1️⃣ Высокая скорость соединения\n"
            f"2️⃣ Легкость в подключении и настройке\n"
            f"3️⃣ Полная анонимность и безопасность данных\n"
            f"<i>🔥 Подключайся и получай максимум от интернета!</i>",
            f"🔗 Доп аргументы при переходе: <i>{command_args}</i>\n",
            reply_markup=main_inline_kb(user_id)
        )

    else:
        await message.answer(
            f"<b>🌐 VPN bot на протоколе VLESS</b>\n"
            f"⚡ <i>Быстрый</i>, <i>надёжный</i>\n"
            f"🎁 <b>3 дня бесплатно</b>, до 3 устройств на 1 ключ\n"
            f"💸 <b>70 рублей</b> за 1 ключ\n"
            f"💎 Есть <b>реферальная система</b>\n"
            f"<b>🚀 Почему выбирают нас:</b>\n"
            f"1️⃣ Высокая скорость соединения\n"
            f"2️⃣ Легкость в подключении и настройке\n"
            f"3️⃣ Полная анонимность и безопасность данных\n"
            f"<i>🔥 Подключайся и получай максимум от интернета!</i>",
            reply_markup=main_inline_kb(user_id)
        )


@router.message(Command('profile'))
async def profile_command(message: Message, state: FSMContext):
    await state.clear()

    user = await UserService.find_one_or_none(telegram_id=str(message.from_user.id))

    ref_link = None
    date_expire = None
    if user is not None:
        await message.answer(
            f" <b>💼 Личный кабинет</b>\n"
            f" <b>💰 Баланс:</b> <i>{user.balance}</i>\n"
            f" <b>📅 Ближайшая дата списания:</b> <i>{date_expire}</i>\n"
            f" <b>🔗 Ваша реферальная ссылка:</b>\n"
            f" <code>https://t.me/vless_tgbot?start={message.from_user.id} </code>\n"
            f" ✨ Используйте реферальную систему, чтобы получить бонусы и подарки!",
            reply_markup=profile_inline_kb()
        )


@router.callback_query(F.data == 'home')
async def page_home(call: CallbackQuery):

    await call.message.edit_text(
        f"<b>🌐 VPN bot на протоколе VLESS</b>\n"
        f"⚡ <i>Быстрый</i>, <i>надёжный</i>\n"
        f"🎁 <b>3 дня бесплатно</b>, до 3 устройств на 1 ключ\n"
        f"💸 <b>70 рублей</b> за 1 ключ\n"
        f"💎 Есть <b>реферальная система</b>\n"
        f"<b>🚀 Почему выбирают нас:</b>\n"
        f"1️⃣ Высокая скорость соединения\n"
        f"2️⃣ Легкость в подключении и настройке\n"
        f"3️⃣ Полная анонимность и безопасность данных\n"
        f"<i>🔥 Подключайся и получай максимум от интернета!</i>",
        reply_markup=main_inline_kb(call.from_user.id)
    )


@router.callback_query(F.data == 'get_profile')
async def get_user_profile(call: CallbackQuery):
    # user service find user from_user.id
    user = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))

    ref_link = None
    date_expire = None
    if user is not None:
        await call.message.edit_text(
            f"<b>💼 Личный кабинет</b>\n"
            f"<b>💰 Баланс:</b> <i>{user.balance}</i>\n"
            f"<b>📅 Ближайшая дата списания:</b> <i>{date_expire}</i>\n"
            f"<b>🔗 Ваша реферальная ссылка:</b> <i>{ref_link}</i>\n"
            f"<i>✨ Используйте реферальную систему, чтобы получить бонусы и подарки!</i>",
            reply_markup=profile_inline_kb()
        )


@router.callback_query(F.data == 'get_server')
async def get_servers(call: CallbackQuery):
    # select
    servers_list = ['Netherlands']
    await call.message.edit_text(
        f"<b>🌍 Выберете сервер</b>",
        reply_markup=servers_inline_kb(servers_list)
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
        if balance <= 0:
            await message.answer("Ошибка. Введите положительное число!")
            return
        await state.update_data(balance=balance)

        # await del_msg(message, state)

        data = await state.get_data()
        # await bot.delete_message(chat_id=message.from_user.id, message_id=data["last_msg_id"])

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
            logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

    await message.edit_text(text="Баланс успешно пополнен!", reply_markup=home_inline_kb())

@router.callback_query(F.data == 'promocode')
async def get_promocode(call: CallbackQuery):
    pass


@router.callback_query(F.data == 'get_all_keys')
async def get_all_user_keys(call: CallbackQuery):
    pass
