from faststream.rabbit.fastapi import RabbitRouter

from app.config import settings, bot
from app.entities.users.service import UserService

router = RabbitRouter(url=settings.get_rabbitmq_url())


@router.subscriber('admin_msg')
async def send_msg_for_admins(msg: str):
    for admin in settings.ADMINS_LIST:
        await bot.send_message(
            chat_id=admin,
            text=msg
        )
        

@router.subscriber('users_msg')
async def send_msg_for_users(msg: str):
    users = await UserService.find_all()
    for user in users:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=msg
            )


@router.subscriber('send_msg')
async def send_msg(msg: dict):
    await bot.send_message(
        chat_id=msg['user_id'],
        text=msg['msg']
        )

# сделать слушателя на очередь отправки уведомлений для оплаты (после 30 дней)