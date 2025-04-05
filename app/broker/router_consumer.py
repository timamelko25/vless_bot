from faststream.rabbit.fastapi import RabbitRouter
from aiogram.types import InlineKeyboardMarkup

from app.config import settings, bot
from app.entities.users.service import UserService
from .schemas import MessageScheme

router = RabbitRouter(url=settings.get_rabbitmq_url())


@router.subscriber("admin_msg")
async def send_msg_for_admins(msg: MessageScheme):
    for admin in settings.ADMINS_LIST:
        await bot.send_message(chat_id=admin, text=msg.message, reply_markup=msg.keyboard)


@router.subscriber("users_msg")
async def send_msg_for_users(msg: MessageScheme):
    users = await UserService.find_all()
    for user in users:
        await bot.send_message(
            chat_id=user.telegram_id, text=msg.message, reply_markup=msg.keyboard
        )


@router.subscriber("send_msg")
async def send_msg(msg: MessageScheme):
    await bot.send_message(
        chat_id=msg.telegram_id, text=msg.message, reply_markup=msg.keyboard
    )


# сделать слушателя на очередь отправки уведомлений для оплаты (после 30 дней)
