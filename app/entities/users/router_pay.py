from datetime import datetime, timedelta, timezone
from loguru import logger
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from app.broker.schemas import MessageScheme
from app.config import bot, settings, broker
from app.entities.keys.service import KeyService
from app.entities.keys.schemas import KeyPayloadScheme
from app.utils.utils import del_msg
from app.entities.payments.service import PaymentService
from app.entities.payments.schemas import PaymentScheme
from .kb import (
    get_key_kb,
    kb_confirm_upd,
    top_up_kb,
    cancel_kb,
    payment_kb,
)
from .service import UserService


router = Router()


class AddBalance(StatesGroup):
    balance = State()
    buying = State()
    confirm = State()


@router.callback_query(F.data == "top_up")
async def update_user_balance(call: CallbackQuery, state: FSMContext):
    await state.clear()
    msg = await call.message.edit_text(
        text=(
            "Введите сумму для пополнения\n\n"
            "Минимальная сумма пополнения 80\n"
            "Максимальная сумма пополнения 10000"
        ),
        reply_markup=cancel_kb(),
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddBalance.balance)


@router.message(F.text, AddBalance.balance)
async def get_balance(message: Message, state: FSMContext):
    try:
        balance = float(message.text.replace(",", ".").strip())
        if balance < 80:
            await del_msg(message, state)
            msg = await message.answer(
                text=(
                    "Ошибка. Минимальная сумма пополнения 80\n"
                    "Введите корректную сумму для пополнения"
                ),
                reply_markup=cancel_kb(),
            )
            await state.update_data(last_msg_id=msg.message_id)
            return
        elif balance > 10000:
            await del_msg(message, state)
            msg = await message.answer(
                text=(
                    "Ошибка. Максимальная сумма пополнения 10000\n"
                    "Введите корректную сумму для пополнения"
                ),
                reply_markup=cancel_kb(),
            )
            await state.update_data(last_msg_id=msg.message_id)
            return
        await state.update_data(balance=balance)

        msg = await message.answer(
            text=(
                f"Баланс будет пополнен на: {balance}₽\n\n"
                "Подтвердите сумму пополнения"
            ),
            reply_markup=kb_confirm_upd(),
        )
        await del_msg(message, state)

        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(AddBalance.confirm)
    except ValueError:
        await message.answer(text="Ошибка. Введите корректный баланс!")
        return


@router.callback_query(F.data == "confirm_add_balance")
async def confirm_add_balance(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()

        user_info = await UserService.find_one_or_none(
            telegram_id=call.from_user.id
        )
        price = data["balance"]

        await call.message.delete()
        await state.set_state(AddBalance.buying)
        
        msg = await bot.send_invoice(
            chat_id=call.from_user.id,
            title=f"Оплата {price}₽",
            description=f"Пожалуйста, завершите оплату в размере {price}₽, чтобы пополнить баланс.",
            payload=f"{user_info.id}_{data['balance']}",
            provider_token=settings.PROVIDER_TOKEN,
            currency="RUB",
            # need_phone_number=True,
            # send_phone_number_to_provider=True,
            need_email=True,
            send_email_to_provider=True,
            start_parameter="test",
            prices=[LabeledPrice(label=f"Оплата {price}", amount=int(price) * 100)],
            reply_markup=payment_kb(price),
        )

        await state.update_data(last_msg_id=msg.message_id)
    except Exception as e:
        logger.error(f"Ошибка при отправке счета на оплату {e}")
        return


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, state: FSMContext):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

    except Exception as e:
        logger.error(f"PreCheckout error: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_q.id, ok=False, error_message="Ошибка при обработке платежа"
        )
        return


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
    # await message.delete()
    # await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('last_msg_id'))
    try:
        await del_msg(message, state)

        payment_info = message.successful_payment

        user_id, balance = payment_info.invoice_payload.split("_")

        payment_data = PaymentScheme(
            user_id=int(user_id),
            payment_id=payment_info.telegram_payment_charge_id,
            sum=payment_info.total_amount / 100,
        )

        user = await UserService.find_one_or_none(id=int(user_id))

        await PaymentService.add_payment_in_history(data=payment_data)

        if user.refer_id:
            user_refer = await UserService.find_one_or_none(telegram_id=user.refer_id)
            await UserService.update_balance_and_count_refer(
                telegram_id=user_refer.telegram_id, balance=float(balance) * 20 / 100
            )
            await UserService.update_balance(
                telegram_id=user.telegram_id, balance=float(balance)
            )
        else:
            await UserService.update_balance(
                telegram_id=user.telegram_id, balance=float(balance)
            )

        user_info = (
            f"@{user.username} ({message.from_user.id})"
            if user.username
            else f"c ID {message.from_user.id}"
        )

        if user.refer_id:
            text = (
                f"💲 Пользователь {user_info} пополнил баланс на {balance}\n"
                f"Пользователь реферальной системы получил бонус {float(balance) * 20 / 100}"
            )
        else:
            text = f"💲 Пользователь {user_info} пополнил баланс на {balance}"

        msg = MessageScheme(message=text)

        await broker.publish(msg, "admin_msg")

        logger.info(f"User {user_info} top up balance for {balance}")
        await message.answer(text="Баланс успешно пополнен!", reply_markup=get_key_kb(),)

        keys = await UserService.find_expiry_keys(telegram_id=message.from_user.id)

        if keys:
            current_time = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            new_time = current_time + timedelta(days=30)
            date = int(new_time.timestamp() * 1000)
            for key in keys:
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
                    await message.answer(text=f"Успешно оплачен ключ {key.email}")
                    logger.info(
                        f"User {user.telegram_id} successfully updated subscription {key.email} for 30 days"
                    )
                else:
                    logger.error(
                        f"Error while updating subscription for key {key.email} for user {user.telegram_id}"
                    )

    except Exception as e:
        logger.error(f"Error for updating key after toped up balance {e}")


@router.message(StateFilter(AddBalance.buying))
async def unsuccessful_payment(message: Message, state: FSMContext):
    await del_msg(message, state)
    msg = await message.answer(
        text="Не удалось выполнить платеж!\nПопробуйте еще раз", reply_markup=top_up_kb()
    )
    await state.update_data(last_msg_id=msg.message_id)
