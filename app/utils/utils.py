from loguru import logger
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import bot


async def del_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get('last_msg_id')

    try:
        if last_msg_id:
            await bot.delete_message(chat_id=message.from_user.id, message_id=last_msg_id)
        else:
            logger.warning("Error: no identifier to last message")
        await message.delete()
    except Exception as e:
        logger.error(f"Error with deleting message: {e}")
