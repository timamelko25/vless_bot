
from faststream.rabbit.fastapi import RabbitRouter

from app.config import settings, bot

router = RabbitRouter(url=settings.get_rabbitmq_url())


@router.subscriber("admin_msg")
async def send_msg_from_admin(msg: str):
    for admin in settings.ADMINS_LIST:
        await bot.send_message(
            chat_id=admin,
            text=msg
        )

# сделать слушателя на очередь отправки уведомлений для оплаты (после 30 дней)