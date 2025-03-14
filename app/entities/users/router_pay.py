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
from app.entities.payments.service import PaymentService
from app.entities.keys.service import KeyService
from app.entities.keys.router_key_get import get_servers
from .kb import gen_key_inline_kb, kb_confirm_upd, home_inline_kb, get_key_inline_kb, cancel_inline_kb, payment_inline_kb
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
        f"Введите сумму для пополнения\n\n"
        f"Минимальная сумма пополнения 80\n"
        f"Максимальная сумма пополнения 10000"
    )

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddBalance.balance)


@router.message(F.text, AddBalance.balance)
async def get_balance(message: Message, state: FSMContext):
    try:
        balance = float(message.text.replace(',', '.').strip())
        if balance < 80:
            await del_msg(message, state)
            msg = await message.answer(
                text=(
                    f"Ошибка. Минимальная сумма пополнения 80\n"
                    f"Введите корректную сумму для пополнения"
                ),
                reply_markup=cancel_inline_kb()
            )
            await state.update_data(last_msg_id=msg.message_id)
            return
        elif balance > 10000:
            await del_msg(message, state)
            msg = await message.answer(
                text=(
                    f"Ошибка. Максимальная сумма пополнения 10000!\n"
                    f"Введите корректную сумму для пополнения"
                ),
                reply_markup=cancel_inline_kb()
            )
            await state.update_data(last_msg_id=msg.message_id)
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
            title=f'Оплата {price}₽',
            description=f'Пожалуйста, завершите оплату в размере {price}₽, чтобы пополнить баланс.',
            payload=f"{user_info.id}_{data['balance']}",
            provider_token=settings.PROVIDER_TOKEN,
            currency='RUB',
            need_phone_number=True,
            send_phone_number_to_provider=True,
            prices=[
                LabeledPrice(
                    label=f'Оплата {price}',
                    amount=int(price) * 100
                )
            ],
            reply_markup=payment_inline_kb(price)
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
            pre_checkout_q.id,
            ok=False,
            error_message="Ошибка при обработке платежа"
        )
        return


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):

    # await message.delete()
    # await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('last_msg_id'))
    try:
        await del_msg(message, state)

        payment_info = message.successful_payment

        user_id, balance = payment_info.invoice_payload.split('_')

        payment_data = {
            'user_id': int(user_id),
            'payment_id': payment_info.telegram_payment_charge_id,
            'sum': payment_info.total_amount / 100,
        }

        user = await UserService.find_one_or_none(id=int(user_id))

        await PaymentService.add_payment_in_history(data=payment_data)

        if user.refer_id:
            user_refer = await UserService.find_one_or_none(telegram_id=user.refer_id)
            await UserService.update_balance_and_count_refer(
                telegram_id=user_refer.telegram_id,
                balance=float(balance) * 20 / 100
            )
            await UserService.update_balance(
                telegram_id=user.telegram_id,
                balance=float(balance)
            )
        else:
            await UserService.update_balance(
                telegram_id=user.telegram_id,
                balance=float(balance)
            )

        user_info = f"@{user.username} ({message.from_user.id})" if user.username else f"c ID {message.from_user.id}"

        for admin_id in settings.ADMINS_LIST:
            try:
                if user.refer_id:
                    text = (
                        f"💲 Пользователь {user_info} пополнил баланс на {balance}\n"
                        f"Пользователь реферальной системы получил бонус {float(balance) * 20 / 100}"
                    )
                else:
                    text = (
                        f"💲 Пользователь {user_info} пополнил баланс на {balance}"
                    )

                await bot.send_message(
                    chat_id=admin_id,
                    text=text
                )

            except Exception as e:
                logger.error(
                    f"Ошибка при отправке уведомления администраторам: {e}")

        logger.info(f"Пользователь {user_info} пополнил баланс на {balance}")
        await message.answer(text="Баланс успешно пополнен!", reply_markup=gen_key_inline_kb())
    except Exception as e:
        logger.error("Ошибка при пополнении баланса после получения оплаты")


@router.message(StateFilter(AddBalance.buying))
async def unsuccessful_payment(message: Message, state: FSMContext):
    await del_msg(message, state)
    await message.answer(
        text="Не удалось выполнить платеж!",
        reply_markup=get_key_inline_kb()
    )
