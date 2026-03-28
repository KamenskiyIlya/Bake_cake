from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)


def admin_main_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Статистика переходов по ссылке',
            callback_data='link_stats')],
        [InlineKeyboardButton(text='Новые заказы',
            callback_data='new_orders')],
        [InlineKeyboardButton(text='Главное меню',
            callback_data='main_menu')],
    ])

    return keyboard


def show_order(order):
    button_text = f"Заказ номер {order['id']}"
    keyboard = [[
        InlineKeyboardButton(
            text=button_text,
            callback_data=f"admin_order_{order['id']}"
    )]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def order_actions(order_id, customer_tg_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить статус',
            callback_data=f'change_status_{order_id}')],
        [InlineKeyboardButton(text='Связаться с клиентом',
            url=f"tg://user?id={customer_tg_id}")],
        [InlineKeyboardButton(text='К списку заказов',
            callback_data='new_orders')],
    ])

    return keyboard