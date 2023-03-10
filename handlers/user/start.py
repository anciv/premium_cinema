from datetime import timedelta
from time import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    ParseMode

import config
from db import UserCommands
from dispatcher import dp, bot
from states import PaymentState

db = UserCommands()
PRICE = types.LabeledPrice(label="Подписка на месяц", amount=1000 * 100)  # in cents


@dp.message_handler(commands=['start', 'menu'])
async def send_welcome(message: types.Message):
    menu_kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    msg = 'Приветсвую, я бот-ассистент для упрощения работы с <a href="https://t.me/api_py">PremiumCinema.</a>\n' \
          'Подписка на месяц стоит 1000₽'

    if await db.user_exists(message.from_user.id):
        msg = 'Выберите действие 👇'
        menu_kb.add(KeyboardButton(text="Моя подписка"))
    else:
        menu_kb = InlineKeyboardMarkup(one_time_keyboard=True)
        menu_kb.add(InlineKeyboardMarkup(text="Заплатить 1000₽", callback_data="buy:month"))

    await message.answer(msg,
                         reply_markup=menu_kb, parse_mode=ParseMode.HTML,
                         disable_web_page_preview=True)

    await PaymentState.first()


@dp.callback_query_handler(text_contains='buy:month', state=PaymentState.action)
async def get_action(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await buy(call.message)


@dp.message_handler(state=PaymentState.action)
async def get_action_subscribed_user(message: types.Message, state: FSMContext):
    await state.finish()
    days = await time_sub_day(message.from_user.id)
    if not days:
        await db.update_user_status(message.from_user.id, False)
        msg = 'Увы, срок вашей подписки истек. Хотите обноваить сроки?'
        menu_kb = InlineKeyboardMarkup(one_time_keyboard=True)
        menu_kb.add(InlineKeyboardMarkup(text="Заплатить 1000₽", callback_data="buy:month"))

        await message.answer(msg, reply_markup=menu_kb)
        await PaymentState.first()
    else:
        status = 'Активный' if await db.is_active(message.from_user.id) else 'Неоплаченный'
        msg = f'<b>Статус:</b> {status}\n' \
              f'<b>Подписка:</b> {days}'
        await message.answer(msg, parse_mode=ParseMode.HTML)


async def buy(message: types.Message):
    await bot.send_invoice(message.chat.id,
                           title="Bot subscription",
                           description="Активация подписки на месяц",
                           provider_token=config.PAYMASTER,
                           currency="rub",
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one_month_subscription",
                           payload="month_sub")


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    if message.successful_payment.invoice_payload == 'month_sub':
        sub_time = int(time()) + days_to_seconds(30)

        if await db.user_exists(message.from_user.id):
            await db.update_sub_days(message.from_user.id, sub_time)
            await db.update_user_status(message.from_user.id, True)
        else:
            await db.add_user(user_id=message.from_user.id, sub_time=sub_time)

        await message.answer(f"Оплата на сумму {message.successful_payment.total_amount //100} "
                             f"{message.successful_payment.currency} произошла успешно")
        await message.answer('Активирована подписка на месяц\n'
                             'Нажмите /menu для наблюдения за статусом подписки')


def days_to_seconds(days):
    return days * 24 * 60 * 60


async def time_sub_day(user_id):
    now = int(time())
    days_left = int(await db.get_sub_days(user_id)) - now
    td = str(timedelta(seconds=days_left))
    td = td.replace('days', 'дней')
    td = td.replace('day', 'день')
    return False if days_left <= 0 else td


@dp.message_handler()
async def all_other(message: types.Message):
    await message.answer('Нажмите /menu для использования')
