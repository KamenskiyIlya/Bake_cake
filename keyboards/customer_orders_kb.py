from aiogram.types import (
	ReplyKeyboardMarkup, KeyboardButton,
	InlineKeyboardMarkup, InlineKeyboardButton)



def all_user_orders(order):
	button_text = f"Заказ номер {order['id']}"
	keyboard = [[
		InlineKeyboardButton(
			text=button_text,
			callback_data=f"order_id_{order['id']}"
	)]]

	return InlineKeyboardMarkup(inline_keyboard=keyboard)


def what_customer_needs():
	keyboard = [
		[
		InlineKeyboardButton(text='Узнать статус', callback_data='check_status'),
		InlineKeyboardButton(text='Повторить заказ', callback_data='repeat_order')
		],
		[InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
	]

	return InlineKeyboardMarkup(inline_keyboard=keyboard)