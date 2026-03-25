from aiogram.types import (
	ReplyKeyboardMarkup, KeyboardButton,
	InlineKeyboardMarkup, InlineKeyboardButton)



def all_user_orders(order):
	button_text = f"Заказ номер {order['id']}"
	keyboard = [
		InlineKeyboardButton(
			text=button_text,
			callback_data=f'order_id_{order['id']}'
	)]

	return InlineKeyboardMarkup(inline_keyboard=keyboard)