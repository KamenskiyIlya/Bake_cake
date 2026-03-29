from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.admin_kb import (
    admin_main_kb,
    show_order,
    order_actions,
    change_order_status_kb,
    after_change_status)
from config import ADMIN_IDS, ORDERS, CUSTOMERS
from handlers.states import AdminStates
from handlers.db_utils import load_db, save_db, get_bot_stats


router = Router()


def is_admin(message: Message):
    return message.from_user.id in ADMIN_IDS


def is_admin_callback(callback: CallbackQuery):
    return callback.from_user.id in ADMIN_IDS


@router.message(F.text == 'Админ-панель', is_admin)
async def admin_panel(message: Message):
    await message.answer(
        'Вы вошли в панель администратора.\n'
        'Выберите действие:',
        reply_markup=admin_main_kb()
    )


@router.callback_query(F.data == 'admin_back', is_admin_callback)
async def admin_back_panel(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            'Вы вошли в панель администратора.\n'
            'Выберите действие:',
            reply_markup=admin_main_kb()
        )
    except Exception as e:
        print(f'При попытке изменить сообщение произошла ошибка {e}')

    await callback.answer()


@router.callback_query(F.data == 'show_stats', is_admin_callback)
async def admin_link_stats(callback: CallbackQuery):
    stats = get_bot_stats()

    await callback.message.answer(
        'Статистика переходов в бота:\n'
        f'Всего запусков (/start): {stats['total_starts']}\n'
        f'Уникальных пользователей: {stats['unique_users']}',
        reply_markup=admin_main_kb()
    )

    await callback.answer()


@router.callback_query(F.data == 'new_orders', is_admin_callback)
async def show_new_orders(callback: CallbackQuery, state: FSMContext):
    new_orders = [order for order in ORDERS if order['status'] != 'Заказ доставлен']

    if not new_orders:
        await callback.message.edit_text(
            'Новых заказов пока нет.',
            reply_markup=admin_main_kb()

        )

        await callback.answer()
        return

    message_ids = []
    info_msg = await callback.message.edit_text('Новые заказы:')
    message_ids.append(info_msg.message_id)
    for order in new_orders:
        order_msg = await callback.message.answer(
            f'#{order["id"]}\n'
            f'{order["product_name"]}\n'
            f'{order["total_price"]}\n'
            f'{order["status"]}\n'
            f'Доставить к {order["deliver_to"]}',
            reply_markup=show_order(order)
        )
        message_ids.append(order_msg.message_id)

    msg = await callback.message.answer(
        'Выберите какой из вышеуказанных заказов Вас интересует?')
    message_ids.append(msg.message_id)
    await state.update_data(order_messages=message_ids)

    await callback.answer()


@router.callback_query(
    F.data.startswith('admin_order_'),
    is_admin_callback)
async def admin_order_details(callback: CallbackQuery, state: FSMContext):
    order_id =int(callback.data.split('_')[2])
    order = next((order for order in ORDERS if order['id'] == order_id), None)
    customer = next(
        (c for c in CUSTOMERS if order['customer_id'] == c['id']),
        None)

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
        'Полная информация по выбранному заказу:\n'
        f'Заказ #{order["id"]}\n'
        f'Клиент: {customer["name"]}\n'
        f'Телефон: {order["phone_number"]}\n'
        f'Торт: {order["product_name"]}\n'
        f'Кастомизация: {order["customization"]}\n'
        f'Примененный промокод: {order['promo_code']}'
        f'Сумма заказа: {order["total_price"]}\n'
        f'Дата заказа: {order["created_at"]}\n'
        f'Доставить к: {order["deliver_to"]}\n'
        f'Адрес доставки: {order["address"]}\n'
        f'Комментарий к заказу: {order["comment"]}\n'
        f'Статус: {order["status"]}',
        reply_markup=order_actions(order_id, customer["telegram_id"])
    )

    await callback.answer()

@router.callback_query(
    F.data.startswith('change_status_'),
    is_admin_callback)
async def change_order_status(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split('_')[2])
    await state.update_data(current_order_id=order_id)
    await state.set_state(AdminStates.waiting_new_status)

    await callback.message.edit_text(
        'Выберите новый статус заказа:',
        reply_markup=change_order_status_kb()
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith('status_'),
    AdminStates.waiting_new_status)
async def admin_set_status(callback: CallbackQuery, state: FSMContext):
    status_list = {
    'notpaid': 'Не оплачен',
    'paid': 'Оплачен',
    'delivery': 'Передан в доставку',
    'delivered': 'Заказ доставлен'
    }

    status_key = callback.data.split('_')[1]
    new_status = status_list.get(status_key)

    data = await state.get_data()
    order_id = data.get("current_order_id")
    db=load_db()
    orders = db.get('orders')
    for order in orders:
        if order['id'] == order_id:
            order['status'] = new_status
            save_db(db)
            break

    await state.clear()

    await callback.message.edit_text(
        f'✅ Статус заказа #{order_id} изменён на: {new_status}',
        reply_markup=after_change_status()
    )

    await callback.answer()