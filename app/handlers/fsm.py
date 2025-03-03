import aiogram
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from create_bot import bot

from keyboards.all_kb import main_inline_kb

class Form(StatesGroup):
    status = State()
    key = State()
    
router = Router()

@router.message(Command('keys'))
async def user_status_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Status: \n Key: \n', reply_markup=main_inline_kb())
    await state.set_state(Form.status)
    
@router.message(F.text, Form.status)
async def capture_status(message: Message, state: FSMContext):
    await state.update_data(status=message.text)
    await message.answer('enter key')
    await state.set_state(Form.key)

@router.message(F.text, Form.key)
async def capture_key(message: Message, state: FSMContext):
    await state.update_data(key=message.text)
    
    data = await state.get_data()
    msg = (f'Status: <b>{data.get("status")} </b> \n Key: <b>{data.get("key")}</b>')
    await message.answer(msg)
    await state.clear