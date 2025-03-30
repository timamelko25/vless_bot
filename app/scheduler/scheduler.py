from datetime import datetime, timezone, timedelta

from loguru import logger
from aiogram.types import Message

from app.config import scheduler
from app.entities.keys.service import KeyService
from app.entities.users.kb import get_key_inline_kb
from app.entities.users.service import UserService


async def subscribe_30_day_expire(message: Message):
    users = await UserService.find_all()
    current_time = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    date = int(current_time.timestamp() * 1000)
    three_days_ms = 3 * 24 * 60 * 60 * 1000  # 3 дня в мс
    tolerance_ms = 6 * 60 * 60 * 1000  # Допустимое отклонение (6 часов) в мс
    one_day_ms = 24 * 60 * 60 * 1000

    for user in users:
        for key in user.keys:
            delta = abs(key.expires_at - date)
            if three_days_ms - tolerance_ms <= delta <= three_days_ms + tolerance_ms:
                await message.answer(
                    text=(
                        "Через 3 дня будет списана сумма за ключи\n"
                        "Проверьте сумму баланса для оплаты ключа\n"
                        "Иначе ключ будет деактивирован до пополнения баланса"
                    ),
                    reply_markup=get_key_inline_kb(),
                )

            elif delta < one_day_ms:
                if user.balance >= 150.0:
                    await UserService.update_balance(
                        telegram_id=user.telegram_id, balance=-150.0
                    )

                    new_time = current_time + timedelta(days=30)
                    date = int(new_time.timestamp() * 1000)

                    data = {
                        "id": key.id_panel,
                        "email": key.email,
                        "limitIp": 3,
                        "totalGB": 107374182400,
                        "expiryTime": date,
                        "enable": True,
                    }

                    info = await KeyService.update_key(data=data, server=key.server)
                    if info:
                        await message.answer(text=f"Успешно оплачен ключ {key.email}")
                        logger.info(f"Пользователь {user.telegram_id} успешно обновил подписку на ключ {key.email} на 30 дней")
                    logger.error(f"Ошибка при обновлении подписки на ключ {key.email} у пользователя {user.telegram_id}")

                elif user.balance < 150:
                    data = {
                        "id": key.id_panel,
                        "email": key.email,
                        "limitIp": 3,
                        "totalGB": 107374182400,
                        "expiryTime": None,
                        "enable": False,
                    }
                    
                    info = await KeyService.update_key(data=data, server=key.server)
                    if info:
                        await message.answer(
                            text=f"Недостаточно средств для оплаты ключа {key.email}"
                            "Пополните баланс для возобновления работы ключа",
                            reply_markup=get_key_inline_kb()
                            )


# добавить проверку при пополении баланса имеются ли ключи дизаблед и сразу списании баланса
