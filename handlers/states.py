from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()
    waiting_date = State()
    waiting_time = State()
    waiting_comment = State()
    waiting_promo = State()


class CustomizationForm(StatesGroup):
    waiting_levels = State()
    waiting_shape = State()
    waiting_topping = State()
    waiting_berries = State()
    waiting_decor = State()
    waiting_message = State()