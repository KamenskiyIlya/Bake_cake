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


def get_promocode_kb():
    decline_btn = InlineKeyboardButton(
        text="Пропустить",
        callback_data="skip_promocode"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [decline_btn],
        ]
    )
    return keyboard


def generate_payment_kb(order_id, payment_url):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить QR",
                    callback_data=f"pay_order_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Оплатить по ссылке",
                    url=payment_url
                )
            ],
            [
                InlineKeyboardButton(
                    text="Проверить оплату", 
                    callback_data=f"check_payment_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )
    return keyboard


def generate_payment_success_kb(order_id=None):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="В главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )
    return keyboard