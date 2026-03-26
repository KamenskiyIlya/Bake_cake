from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb():
    keyboard=[
        [
            KeyboardButton(text="Мои заказы"),
            KeyboardButton(text="Заказать торт")
        ],
        [
            KeyboardButton(text="Админ-панель"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню')