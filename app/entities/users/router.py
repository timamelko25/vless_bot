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
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    user = await UserService.find_one_or_none(telegram_id=user_info.telegram_id)
    if user:
        await UserService.add(user_info)

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

    user = await UserService.find_one_or_none(telegram_id=message.from_user.id)

    ref_link = None
    date_expire = None
    await message.answer(
        f"<b>💼 Личный кабинет</b>\n"
        f"<b>💰 Баланс:</b> <i>{user.balance}</i>\n"
        f"<b>📅 Ближайшая дата списания:</b> <i>{date_expire}</i>\n"
        f"<b>🔗 Ваша реферальная ссылка:</b> <i>{ref_link}</i>\n"
        f"✨ Используйте реферальную систему, чтобы получить бонусы и подарки!</i>",
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
    user = await UserService.find_one_or_none(telegram_id=call.from_user.id)

    ref_link = None
    date_expire = None

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

    await call.message.edit_text(
        f"Введите сумму для пополнения",
        reply_markup=prices_reply_kb()
    )

    await state.update_data(last_msg_id=call.message.id)
    await state.set_state(AddBalance.balance)


@router.message(F.text, AddBalance.balance)
async def get_balance(message: Message, state: FSMContext):
    try:
        balance = message.text
        await state.update_data(balance=balance)
        await del_msg(message, state)

        data = await state.get_data()

        text = (
            f"Баланс будет пополнен на:\n"
            f"{data['balance']}"
        )
        msg = await message.edit_text(text=text, reply_markup=kb_confirm_upd())

        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(AddBalance.confirm)
    except ValueError:
        await message.edit_text(text="Ошибка. Введите корректный баланс!")


@router.callback_query(F.data == 'confirm_add_balance')
async def confirm_add_balance(call: CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data['last_msg_id'])
    del data['last_msg_id']
    
    user_info = await UserService.find_one_or_none(id=call.from_user.id)
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
    invoice = True
    if invoice:
        UserService.update(id=call.from_user.id, balance=data['balance'])
        await call.message.edit_text(text="Баланс успешно пополнен!", reply_markup=home_inline_kb())


@router.callback_query(F.data == 'promocode')
async def get_promocode(call: CallbackQuery):
    pass


@router.callback_query(F.data == 'get_all_keys')
async def get_all_user_keys(call: CallbackQuery):
    pass
