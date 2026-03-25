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


def generate_request_contact_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def generate_skip_comment_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить комментарий", callback_data="skip_comment")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ])
    return keyboard