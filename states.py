from aiogram.dispatcher.filters.state import StatesGroup, State


class PaymentState(StatesGroup):
    action = State()
