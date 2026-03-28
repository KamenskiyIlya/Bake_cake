from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_IDS


def main_menu_kb(user_id = None):
    keyboard=[
        [
            KeyboardButton(text="Мои заказы"),
            KeyboardButton(text="Заказать торт")
        ]
    ]

    if user_id and user_id in ADMIN_IDS:
        keyboard.append([
            KeyboardButton(text="Админ-панель")
        ])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню',
        one_time_keyboard=True
    )