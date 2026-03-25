from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb():
    keyboard=[
        [
            KeyboardButton(text="Посмотреть готовый торт"),
            KeyboardButton(text="Создать кастомизированный торт")
        ],
        [
            KeyboardButton(text="Мои заказы"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню')