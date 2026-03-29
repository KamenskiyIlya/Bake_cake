from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.db_utils import load_db


def main_menu_kb(user_id = None):
    keyboard=[
        [
            KeyboardButton(text="Мои заказы"),
            KeyboardButton(text="Заказать торт")
        ]
    ]

    db = load_db()
    admins = db.get('admins', [])
    admin_ids = [admin["telegram_id"] for admin in admins]

    if user_id and user_id in admin_ids:
        keyboard.append([
            KeyboardButton(text="Админ-панель")
        ])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню',
        one_time_keyboard=True
    )