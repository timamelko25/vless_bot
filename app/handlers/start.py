from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.scripts import open_session

from keyboards.all_kb import main_kb, number_kb, simple_inline_kb, main_inline_kb
from keyboards.all_kb import main_inline_kb, profile_inline_kb, servers_inline_kb, keys_inline_kb

from filters.dependencies import IsAdmin

from sqlalchemy import select

from db_handler.models import Users, Servers

from create_bot import admins

from datetime import date

start_router = Router()

# # start bot with /start with tracking
# @start_router.message(CommandStart())
# async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
#     await state.clear()
#     command_args: str = command.args
#     if command_args:
#         await message.answer(
#         f'Start msg with /start using filter CommandStart() with tag {command_args}',
#         reply_markup=main_kb(message.from_user.id)
#         )
#     else:
#         await message.answer(
#             'Start msg with /start using filter CommandStart()',
#             reply_markup=main_kb(message.from_user.id)
#             )
        
@start_router.message(CommandStart())
async def start_command(message: Message, command: CommandObject):
    command_args: str = command.args
    if command_args:
        await message.answer(
            f"VPN bot на протоколе VLESS\n"
            f"3 дня бесплатно, до 3 устройств на 1 ключ\n"
            f"70 бурлей 1 ключ\n"
            f"Есть реф система\n"
            f"{command_args}",
            reply_markup=main_inline_kb()
            )
    else:
        await message.answer(
            f"VPN bot на протоколе VLESS\n"
            f"Быстрый надежный кайф\n"
            f"3 дня бесплатно, до 3 устройств на 1 ключ\n"
            f"70 бурлей 1 ключ\n"
            f"Есть реф система\n",
            reply_markup=main_inline_kb()
            )

@start_router.message(Command('profile'))
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

@start_router.callback_query(F.data == 'main_menu')
async def get_main_menu(call: CallbackQuery):
    await call.message.answer(
            f"VPN bot на протоколе VLESS\n"
            f"Быстрый надежный кайф\n"
            f"3 дня бесплатно, до 3 устройств на 1 ключ\n"
            f"70 бурлей 1 ключ\n"
            f"Есть реф система\n",
            reply_markup=main_inline_kb()
            )

@start_router.callback_query(F.data == 'get_profile')
async def get_profile(call: CallbackQuery):
    user = select(Users).filter_by(id=call.from_user.id)
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
    
@start_router.callback_query(F.data == 'get_server')
async def get_server(call: CallbackQuery):
    # servers = select(Servers).scalar().all()
    # servers_list = [server.name for server in servers]
    servers_list = ['Netherlands']
    await call.message.answer(
        f"Выберете сервер\n",
        reply_markup=servers_inline_kb(servers_list)
        )

@start_router.callback_query(F.data == 'get_key')
async def get_key(call: CallbackQuery):
    
    key=None
    await call.message.answer(
        f"Ваш ключ\n"
        f"{key}",
        reply_markup=keys_inline_kb()
        )
    
    
    
    
    
@start_router.callback_query(F.data == 'test')
async def test(call:CallbackQuery):
    await call.message.answer(
        text="None",
        reply_markup=main_inline_kb()
        )
    

# # start bot with exec command
# @start_router.message(Command('start_2'))
# async def cmd_start_2(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer('Start msg with /start_2 using filter Command()')
   

# # start bot with any text with magic filter
# @start_router.message(F.text == '/start_3')
# async def cmd_start_3(message: Message):
#     await message.answer(
#         'Start msg with /start_3 using magic filter F.text',
#         reply_markup=number_kb()
#         )
    
# @start_router.message(F.text == 'inline')
# async def get_inline_buttons(message: Message):
#     await message.answer('Get text', reply_markup=simple_inline_kb())
    
# @start_router.message(F.text == 'main menu')
# async def get_home_menu(message: Message):
#     await message.answer('Main menu', reply_markup=main_inline_kb())
    
# @start_router.callback_query(F.data == 'get_data')
# async def get_data_from_server(call: CallbackQuery):
#     result = open_session()
#     formatted_message = (f"<b>SMILE FACE:</b> {result}\n"
#                          "<b>thats all</b>"
#                          )
#     await call.message.answer(formatted_message)
    
# @start_router.callback_query(F.data == 'back_home')
# async def get_home(call: CallbackQuery):
#     await call.message.edit_text(
#         text='Main menu',
#         reply_markup=main_inline_kb()
#         )
    
# @start_router.message(Command(commands=["settings", "about"]))
# async def custom_cmd_handler(message: Message, command: CommandObject):
#     command_args: str = command.args
#     command_name = 'settings' if 'settings' in message.text else 'about'
#     response = f'/{command_name} was called'
#     if command_args:
#         response += f' with tag <b>{command_args}'
#     else:
#         response += f' without tag'
#     await message.answer(response)
    
    
# @start_router.message(F.text == 'admin tool', IsAdmin(admins))
# async def handler_admin_msg(message: Message):
#     await message.answer('send msg to admin for admin tool')
    
    
'''
F.data.starstwith('qst_) - magic method to react on CallData with start str (qst_)

F.text
F.photo
F.video
F.animation
F.contact
F.document
F.data (with CallData)
'''