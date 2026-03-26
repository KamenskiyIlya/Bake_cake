from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from config import CAKES, CAKE_OPTIONS


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


def generate_levels_kb():
    keyboard = []
    for level in CAKE_OPTIONS["levels"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{level['name']} (+{level['price_add']}₽)", 
            callback_data=f"level_{level['id']}"
        )])
    keyboard.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_custom")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_shapes_kb():
    keyboard = []
    for shape in CAKE_OPTIONS["shapes"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{shape['name']} (+{shape['price_add']}₽)", 
            callback_data=f"shape_{shape['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_toppings_kb():
    keyboard = []
    for topping in CAKE_OPTIONS["toppings"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{topping['name']} (+{topping['price_add']}₽)", 
            callback_data=f"topping_{topping['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_berries_kb():
    keyboard = []
    keyboard.append([InlineKeyboardButton(text="Без ягод", callback_data="berry_none")])
    for berry in CAKE_OPTIONS["berries"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{berry['name']} (+{berry['price_add']}₽)", 
            callback_data=f"berry_{berry['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_decor_kb():
    keyboard = []
    keyboard.append([InlineKeyboardButton(text="Без декора", callback_data="decor_none")])
    for decor in CAKE_OPTIONS["decorations"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{decor['name']} (+{decor['price_add']}₽)", 
            callback_data=f"decor_{decor['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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