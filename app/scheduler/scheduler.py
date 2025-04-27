from datetime import datetime, timezone, timedelta

from loguru import logger

from app.config import broker, bot
from app.entities.keys.service import KeyService
from app.entities.users.kb import get_key_inline_kb
from app.entities.users.service import UserService
from app.entities.keys.schemas import KeyPayloadScheme
from app.broker.schemas import MessageScheme


async def subscribe_30_day_expire():
    """Automated subscription management for user keys.

    Performs daily checks to:
    - Send 3-day payment reminders for expiring keys
    - Auto-renew subscriptions for users with sufficient balance
    - Disable keys for users with insufficient balance

    Handles all active users and their keys, operating on Moscow time basis
    (15:00 Moscow time daily check). Converts time to UTC for processing.
    """
    logger.info("Start updating keys")
    users = await UserService.find_all()

    moscow_time = datetime.now(timezone.utc) + timedelta(hours=3)
    target_moscow_15 = moscow_time.replace(hour=15, minute=0, second=0, microsecond=0)
    current_time_utc = target_moscow_15 - timedelta(hours=3)

    for user in users:
        for key in user.keys:
            key_expire_time = datetime.fromtimestamp(
                int(key.expires_at)//1000, tz=timezone.utc
            )
            diff = key_expire_time - current_time_utc
            logger.info(key_expire_time)
            logger.info(current_time_utc)
            logger.info(diff)
            if (
                timedelta(days=3) - timedelta(hours=7)
                <= diff
                <= timedelta(days=3) + timedelta(hours=7)
            ):
                msg = MessageScheme(
                    message=(
                        "Через 3 дня будет списана сумма за ключи\n"
                        "Проверьте сумму баланса для оплаты ключа\n"
                        "Иначе ключ будет деактивирован до пополнения баланса"
                    ),
                    telegram_id=user.telegram_id,
                    keyboard=get_key_inline_kb(),
                )
                await broker.publish(msg, "send_msg")

            elif diff <= timedelta(days=1):
                new_time = current_time_utc + timedelta(days=30)
                date = int(new_time.timestamp() * 1000)
                if user.balance >= 150.0:
                    await UserService.update_balance(
                        telegram_id=user.telegram_id, balance=-150.0
                    )

                    data = KeyPayloadScheme(
                        id=key.id_panel,
                        email=key.email,
                        limitIp=3,
                        totalGb=107374182400,
                        expiryTime=str(date),
                        status=True,
                    )

                    info = await KeyService.update_key(data=data, server=key.server)
                    if info:
                        msg = MessageScheme(
                            message=f"Успешно оплачен ключ {key.email}",
                            telegram_id=user.telegram_id,
                        )
                        await broker.publish(msg, "send_msg")
                        logger.info(
                            f"Пользователь {user.telegram_id} успешно обновил подписку на ключ {key.email} на 30 дней"
                        )
                    else:
                        logger.error(
                            f"Ошибка при обновлении подписки на ключ {key.email} у пользователя {user.telegram_id}"
                        )

                elif user.balance < 150:
                    data = KeyPayloadScheme(
                        id=key.id_panel,
                        email=key.email,
                        limitIp=3,
                        totalGb=107374182400,
                        expiryTime=str(1),
                        status=False,
                    )

                    info = await KeyService.update_key(data=data, server=key.server)
                    if info:
                        msg = MessageScheme(
                            message=f"Недостаточно средств для оплаты ключа {key.email}\n"
                            "Пополните баланс для возобновления работы ключа",
                            telegram_id=user.telegram_id,
                            keyboard=get_key_inline_kb(),
                        )
                        await broker.publish(msg, "send_msg")
