from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from config import CAKES


def generate_cake_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for cake in CAKES:
        button_text = f"{cake['name']} — {cake['price']}₽"
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(
                text=button_text, 
                callback_data=f"cake_{cake['id']}"
            )]
        )

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Главное меню", callback_data="main_menu")
    ])
    
    return keyboard