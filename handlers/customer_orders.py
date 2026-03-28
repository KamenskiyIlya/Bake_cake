from aiogram import Router, F, types
from keyboards.customer_orders_kb import (
    show_user_order, what_customer_needs, old_address_kb, first_order_kb)
from keyboards.menu import main_menu_kb
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext


from config import ORDERS, CAKES, CUSTOMERS
from handlers.states import OrderForm

from datetime import datetime


router = Router()

STATUSES = {
    'Оплачен': (
        '✅ Оплачен\n\n'
        'Спасибо! Оплата успешно получена.\n'
        'Мы передали заказ в работу.\n'
        'Торт будет изготовлен и доставлен к указанной дате.'
    ),
    'Передан в доставку': (
        '🚚 Передан в доставку\n\n'
        'Заказ передан службе доставки.\n'
        'В скором времени с Вами свяжется курьер и сообщит более точную информацию.'
    ),
    'Заказ доставлен': (
        '📦 Доставлен\n\n'
        'Заказ доставлен получателю.\n'
        'Благодарим за покупку!'
    ),
}


@router.message(F.text == "Мои заказы")
async def show_orders(message: Message, state: FSMContext):
    user_id = message.from_user.id
    order = next((order for order in ORDERS if order['id'] == order_id), None)
    customer = None
    for client in CUSTOMERS:
        if str(client.get('telegram_id')) == str(user_id):
            customer = client
            break
    if not customer:
        await message.answer(
            'Вы у нас ещё не делали заказы',
            reply_markup=first_order_kb())
        return

    await state.update_data(customer=customer)
    user_orders = []

    message_ids = []
    info_msg = await message.answer('Ваши заказы:')
    message_ids.append(info_msg.message_id)

    for order in ORDERS:
        if customer['id'] == order['customer_id']:
            order_msg = await message.answer(
                f'Заказ номер: {order["id"]}\n'
                f'Название торта: {order["product_name"]}\n'
                f'Общая сумма: {order["total_price"]}\n'
                f'Дата заказа: {order["created_at"]}\n'
                f'Дата доставки: {order["deliver_to"]}\n'
                f'Адрес доставки: {order["address"]}\n'
                f'Статус: {order["status"]}',
                reply_markup=show_user_order(order=order)
            )
            user_orders.append(order)
            message_ids.append(order_msg.message_id)

    await state.update_data(order_messages=message_ids)

    if user_orders:
        msg = await message.answer(
            'Выберите какой из вышеуказанных заказов Вас интересует?')
        message_ids.append(msg.message_id)
        await state.update_data(order_messages=message_ids)
    else:
        await message.answer(
            'У Вас пока не было заказов',
            reply_markup=first_order_kb())


@router.callback_query(F.data.startswith('order_id_'))
async def chose_order(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split('_')[2])
    await state.update_data(order_id=order_id)

    state_data = await state.get_data()
    message_ids = state_data.get('order_messages', [])

    for msg_id in message_ids:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=msg_id
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")

    await callback.message.answer(
        f'Вы выбрали заказ c номером: {order_id}\n'
        f'Название торта: {order["product_name"]}\n'
        f'Общая сумма: {order["total_price"]}\n'
        f'Дата заказа: {order["created_at"]}\n'
        f'Дата доставки: {order["deliver_to"]}\n'
        f'Адрес доставки: {order["address"]}\n'
        f'Статус: {order["status"]}\n\n'
        'Выберите, что Вас интересует',
        reply_markup=what_customer_needs())

    await callback.answer()


@router.callback_query(F.data == 'check_status')
async def check_status_order(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    order_id = state_data.get('order_id')
    customer = state_data.get('customer')

    current_order = find_order_by_id(order_id)
    order_status = current_order['status']

    current_datetime = datetime.now()
    diliver_date = current_order['deliver_to']
    diliver_datetime = datetime.strptime(diliver_date, '%d.%m.%Y %H:%M')

    try:
        await callback.message.delete()
    except Exception as e:
        print(f'Ошибка при удалении сообщения: {e}')

    if current_datetime < diliver_datetime:
        await callback.message.answer(
            f"Статус заказа с номером {order_id}:\n\n"
            f'{STATUSES[order_status]}',
            reply_markup=main_menu_kb(callback.from_user.id))

    elif (current_datetime > diliver_datetime 
        and order_status != 'Заказ доставлен'):
            await callback.message.answer(
                f"Статус заказа с номером {order_id}:\n{order_status}\n\n"
                f"Уважаемый(ая) {customer['name']}!\n\n"
                "Приносим искренние извинения: доставка вашего заказа задерживается.\n"
                "Мы хотим, чтобы торт оказался у вас в идеальном состоянии,"
                "поэтому уделяем большое внимание упаковке и свежести.\n"
                "Постараемся доставить как можно быстрее.\n"
                "Спасибо за понимание и терпение!\n\n"
                "Ваша кондитерская Bake Cake.🍰",
                reply_markup=main_menu_kb(callback.from_user.id))
    else:
        await callback.message.answer(
            f"Статус заказа с номером {order_id}:\n\n"
            f'{STATUSES[order_status]}',
            reply_markup=main_menu_kb(callback.from_user.id))

    await callback.answer()


@router.callback_query(F.data == 'repeat_order')
async def repeat_order(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    order_id = state_data.get('order_id')
    order = find_order_by_id(order_id)
    customer = state_data.get('customer')
    cake = next(
        (cake for cake in CAKES if cake['id'] == order['product_id']),
        None)

    try:
        await callback.message.delete()
    except Exception as e:
        print(f'Ошибка при удалении сообщения: {e}')

    if not cake:
        await callback.message.answer(
            'Торт из заказа больше не доступен.',
            reply_markup=main_menu_kb(callback.from_user.id))
        await callback.answer()
        return

    await state.update_data(
        selected_cake=cake,
        name=customer['name'],
        phone=customer['phone_number'],
        address=order['address'],
        total_price=order['total_price'])

    await state.set_state(OrderForm.waiting_address)

    old_address = order['address']
    await callback.message.answer(
        f"Повторяем заказ #{order_id}\n\n"
        f"Торт: {cake['name']}\n"
        f"Стоимость: {order['total_price']}₽\n\n"
        f"Предыдущий адрес: {old_address}\n"
        "Введите адрес доставки (можно изменить, если нужно)\n"
        "Нажмите на кнопку со старым адресом, если нужно оставить его",
        reply_markup=old_address_kb(order['address'])
    )

    await callback.answer()


@router.message(F.text == "Отмена повторного заказа", OrderForm.waiting_address)
async def cancel_repeat_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Повтор заказа отменён.",
        reply_markup=main_menu_kb(message.from_user.id))


def find_order_by_id(order_id):
    for order in ORDERS:
        if str(order['id']) == str(order_id):
            return order
    return None