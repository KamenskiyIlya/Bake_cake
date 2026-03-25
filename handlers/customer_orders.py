from aiogram import Router, F, types
from keyboards.customer_orders_kb import all_user_orders
from aiogram.types import CallbackQuery

from config import ORDERS


router = Router()


@router.message(F.text == "Мои заказы")
async def show_orders(message: types.Message):
	await message.answer("Я тебя вижу")
	user_id = message.from_user.id
	user_orders = []

	for order in ORDERS:
		if user_id == order['user_id']:
			await message.answer(
				f'Заказ номер: {order["id"]}\n'
				f'Название торта: {order["product_name"]}\n'
				f'Общая сумма: {order["total_price"]}\n'
				f'Дата заказа: {order["created_at"]}\n'
				f'Адрес доставки: {order["address"]}\n'
				f'Статус: {order["status"]}',
				reply_markup=all_user_orders(order=order)
			)
			user_orders.append(order)

	if user_orders:
		await message.answer(
			'Выберите какой из вышеуказанных заказов Вас интересует?'
		)
	else:
		await message.answer('У Вас пока не было заказов')