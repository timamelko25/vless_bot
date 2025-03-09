import asyncio
from datetime import datetime

from loguru import logger
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from app.config import bot, settings
from app.utils.utils import del_msg
from app.entities.servers.service import ServerService
from app.entities.keys.service import KeyService
from .kb import kb_confirm_upd, home_inline_kb, get_key_inline_kb, cancel_kb
from .schemas import NewUserScheme
from .service import UserService


router = Router()


class AddBalance(StatesGroup):
    balance = State()
    buying = State()
    confirm = State()


@router.callback_query(F.data == 'top_up')
async def update_user_balance(call: CallbackQuery, state: FSMContext):

    msg = await call.message.edit_text(
        f"Введите сумму для пополнения"
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddBalance.balance)


@router.message(F.text, AddBalance.balance)
async def get_balance(message: Message, state: FSMContext):
    try:
        balance = float(message.text.replace(',', '.').strip())
        if balance < 10:
            await message.answer("Ошибка. Минимальная сумма пополнения 10")
            return
        elif balance > 10000:
            await message.answer("Ошибка. Максимальная сумма пополнения 10000!")
            return
        await state.update_data(balance=balance)

        data = await state.get_data()

        text = (
            f"Баланс будет пополнен на:\n"
            f"{data['balance']}₽"
        )
        msg = await message.answer(text=text, reply_markup=kb_confirm_upd())
        await del_msg(message, state)

        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(AddBalance.confirm)
    except ValueError:
        await message.answer(text="Ошибка. Введите корректный баланс!")
        return


@router.callback_query(F.data == 'confirm_add_balance')
async def confirm_add_balance(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()

        user_info = await UserService.find_one_or_none(telegram_id=str(call.from_user.id))
        price = data['balance']

        await call.message.delete()
        await state.set_state(AddBalance.buying)
        msg = await bot.send_invoice(
            chat_id=call.from_user.id,
            title=f'Оплата 👉 {price}₽',
            description=f'Пожалуйста, завершите оплату в размере {price}₽, чтобы пополнить баланс.',
            payload=f"{user_info.telegram_id}_{data['balance']}",
            provider_token=settings.PROVIDER_TOKEN,
            currency='rub',
            need_phone_number=True,
            send_phone_number_to_provider=True,
            prices=[
                LabeledPrice(
                    label=f'Оплата {price}',
                    amount=int(price) * 100
                )
            ],
            reply_markup=cancel_kb(price)
        )

        await state.update_data(last_msg_id=msg.message_id)
    except Exception as e:
        logger.error(f"Ошибка при отправке счета на оплату {e}")


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, state: FSMContext):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
    except Exception as e:
        logger.error(f"PreCheckout error: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_q.id,
            ok=False,
            error_message="Ошибка при обработке платежа"
        )


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):

    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('last_msg_id'))

    payment_info = message.successful_payment

    user_id, balance = payment_info.invoice_payload.split('_')

    payment_data = {
        'user_id': str(user_id),
        'payment_id': payment_info.telegram_payment_charge_id,
        'price': payment_info.total_amount / 100,
        'balance': float(balance)
    }

    # добавить оплату в историю payments

    user = await UserService.find_one_or_none(telegram_id=user_id)

    if user.refer_id:
        user_refer = await UserService.find_one_or_none(telegram_id=user.refer_id)
        await UserService.update_balance_and_count_refer(
            telegram_id=user_refer.telegram_id,
            balance=float(balance * 20 / 100)
        )
    else:
        await UserService.update_balance(
            telegram_id=user_id,
            balance=float(balance)
        )

    for admin_id in settings.ADMINS_LIST:
        try:
            username = message.from_user.username
            user_info = f"@{username} ({message.from_user.id})" if username else f"c ID {message.from_user.id}"

            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f"💲 Пользователь {user_info} пополнил баланс на {balance}"
                )
            )
        except Exception as e:
            logger.error(
                f"Ошибка при отправке уведомления администраторам: {e}")

    logger.info(f"Пользователь {user_info} пополнил баланс на {balance}")
    await message.answer(text="Баланс успешно пополнен!", reply_markup=home_inline_kb())


@router.message(StateFilter(AddBalance.buying))
async def unsuccessful_payment(message: Message, state: FSMContext):
    await message.answer(
        text="Не удалось выполнить платеж!",
        reply_markup=get_key_inline_kb()
    )
