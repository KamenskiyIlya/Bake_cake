from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)


def admin_main_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Статистика переходов по ссылке',
            callback_data='show_stats')],
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
        [InlineKeyboardButton(text='Вернуться в панель админа',
            callback_data='admin_back')],
    ])

    return keyboard


def change_order_status_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Не оплачен',
            callback_data='status_notpaid')],
        [InlineKeyboardButton(text='Оплачен',
            callback_data='status_paid')],
        [InlineKeyboardButton(text='Передан в доставку',
            callback_data='status_delivery')],
        [InlineKeyboardButton(text='Доставлен',
            callback_data='status_delivered')],
        [InlineKeyboardButton(text='Вернуться в панель админа',
            callback_data='admin_back')],
    ])

    return keyboard


def after_change_status():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться в панель админа',
            callback_data='admin_back')],
        [InlineKeyboardButton(text='Вернуться к заказам',
            callback_data='new_orders')],
    ])

    return keyboard