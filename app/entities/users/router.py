from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext

from loguru import logger

from app.config import bot, settings

from .kb import main_inline_kb, keys_inline_kb, profile_inline_kb, servers_inline_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    user_id = message.from_user.id
    # с помощью сервиса поискать был ли уже этот человек
    user_info = 5
    # схема пидантик для проверки
    # values = UserModel(
    #     telegram_id=user_id,
    #     username=message.from_user.username,
    #     first_name=message.from_user.first_name,
    #     last_name=message.from_user.last_name,
    # )
    # Userservice.add new user

    command_args: str = command.args

    if command_args:
        await message.answer(
            f"VPN bot на протоколе VLESS\n"
            f"3 дня бесплатно, до 3 устройств на 1 ключ\n"
            f"70 рублей 1 ключ\n"
            f"Есть реф система\n"
            f" Доп аргументы при переходе {command_args}",
            reply_markup=main_inline_kb(user_id)
        )

    else:
        await message.answer(
            f"VPN bot на протоколе VLESS\n"
            f"Быстрый надежный кайф\n"
            f"3 дня бесплатно, до 3 устройств на 1 ключ\n"
            f"70 бурлей 1 ключ\n"
            f"Есть реф система\n",
            reply_markup=main_inline_kb(user_id)
        )
        
        
@router.message(Command('profile'))
async def profile_command(message: Message):
    #user = select(Users).filter_by(id=message.from_user.id)
    ref_link = None
    date_expire = None
    await message.answer(
        f"Личный кабинет\n"
        f"\n"
        f"Баланс\n"
        f"Ближайшая дата списания {date_expire}\n"
        f"Ваша реферальная ссылка\n"
        f"{ref_link}",
        reply_markup=profile_inline_kb()
        )
    

@router.callback_query(F.data == 'back')
async def get_back(call: CallbackQuery, state: FSMContext):
    pass


@router.callback_query(F.data == 'home')
async def page_home(call: CallbackQuery):
    await call.answer("Главная страница")
    await call.message.answer(
        f"VPN bot на протоколе VLESS\n"
        f"3 дня бесплатно, до 3 устройств на 1 ключ\n"
        f"70 рублей 1 ключ\n"
        f"Есть реф система\n",
        reply_markup=main_inline_kb(call.from_user.id)
    )


@router.callback_query(F.data == 'get_profile')
async def get_user_profile(call: CallbackQuery):
    # user service find user from_user.id
    user = 4
    ref_link = None
    date_expire = None
    await call.message.answer(
        f"Личный кабинет\n"
        f"\n"
        f"Баланс\n"
        f"Ближайшая дата списания {date_expire}\n"
        f"Ваша реферальная ссылка\n"
        f"{ref_link}",
        reply_markup=profile_inline_kb()
        )


@router.callback_query(F.data == 'get_server')
async def get_servers(call: CallbackQuery):
    servers_list = ['Netherlands']
    await call.message.answer(
        f"Выберете сервер\n",
        reply_markup=servers_inline_kb(servers_list)
        )
    
    
@router.callback_query(F.data == 'top_up')
async def update_user_balance(call: CallbackQuery):
    pass

@router.callback_query(F.data == 'promocode')
async def get_promocode(call: CallbackQuery):
    pass

@router.callback_query(F.data == 'get_all_keys')
async def get_all_user_keys(call: CallbackQuery):
    pass