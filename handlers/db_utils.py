import json
from datetime import datetime

from config import CONFIG_PATH, ORDERS, CUSTOMERS


def save_to_json():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    db['orders'] = ORDERS
    db['customers'] = CUSTOMERS

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def create_or_find_customer(tg_id, name, phone, address):
    for customer in CUSTOMERS:
        if customer['telegram_id'] == tg_id:
            if (customer['name'] != name
                or customer['phone_number'] != phone
                or customer['address'] != address):
                    customer['name'] = name
                    customer['phone_number'] = phone
                    save_to_json()
            return customer

    new_id = max([customer['id'] for customer in CUSTOMERS], default=0) + 1
    new_customer = {
        'id': new_id,
        'telegram_id': tg_id,
        'name': name,
        'phone_number': phone,
        'address': address,
    }
    CUSTOMERS.append(new_customer)
    save_to_json()

    return new_customer


def create_order(order_data):
    new_id = max([order['id'] for order in ORDERS], default=0) + 1
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%d.%m.%Y %H:%M')

    new_order = {
        'id': new_id,
        'customer_id': order_data['customer_id'],
        'product_id': order_data['product_id'],
        'product_name': order_data['product_name'],
        'customization': order_data['customization'],
        'total_price': order_data['total_price'],
        'created_at': formatted_datetime,
        'deliver_to': f"{order_data['date']} {order_data['time']}",
        'status': 'Не оплачен',
        'phone_number': order_data['phone_number'],
        'address': order_data['address'],
        'comment': order_data['comment']
    }

    ORDERS.append(new_order)
    save_to_json()

    return new_order