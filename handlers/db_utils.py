import json
from datetime import datetime

from config import CONFIG_PATH, ORDERS, CUSTOMERS, PROMO_CODES


def load_db():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db=None):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def get_promo_codes():
    db = load_db()
    return db.get("promo_codes", [])


def get_valid_promo(promo_code):
    promo_codes = get_promo_codes()
    promo = next((p for p in promo_codes if p["code"].upper() == promo_code.upper()), None)
    
    if not promo:
        return None
    
    promo_data = next((p for p in promo_codes if p["code"] == promo["code"]), promo)

    if not promo_data.get("conditions", {}).get("is_active", True):
        return None

    conditions = promo_data["conditions"]
    if conditions.get("uses_count", 0) >= conditions.get("max_uses", float('inf')):
        return None
    
    return promo_data


def increase_promo_usage(promo_code):
    db = load_db()
    promo_codes = db.get("promo_codes", [])
    
    for promo in promo_codes:
        if promo["code"] == promo_code:
            promo["conditions"]["uses_count"] = promo["conditions"].get("uses_count", 0) + 1
            break
    
    save_db(db)


def apply_promo_discount(price, promo_code=None):
    if not promo_code:
        return price, 0, None
    
    promo = get_valid_promo(promo_code)
    if not promo:
        return price, 0, None

    if price < promo["min_order"]:
        return price, 0, f"Минимальная сумма: {promo['min_order']}₽"
    
    discount_percent = promo["discount_percent"]
    discount_amount = int(price * discount_percent / 100)
    final_price = price - discount_amount

    increase_promo_usage(promo_code)
    
    return final_price, discount_amount, promo


def create_or_find_customer(tg_id, name, phone, address):
    db = load_db()
    customers = db.get("customers", [])

    for customer in customers:
        if customer.get('telegram_id') == tg_id:
            updated = False
            if customer.get('name') != name:
                customer['name'] = name
                updated = True
            if customer.get('phone_number') != phone:
                customer['phone_number'] = phone
                updated = True
            if customer.get('address') != address:
                customer['address'] = address
                updated = True
                
            if updated:
                save_db(db)
            return customer

    new_id = max([c.get('id', 0) for c in customers], default=0) + 1
    new_customer = {
        'id': new_id,
        'telegram_id': tg_id,
        'name': name,
        'phone_number': phone,
        'address': address,
    }
    customers.append(new_customer)
    db["customers"] = customers
    save_db(db)
    CUSTOMERS[:] = db["customers"]

    return new_customer


def create_order(order_data):
    db = load_db()
    orders = db.get("orders", [])
    
    new_id = max([order.get('id', 0) for order in orders], default=0) + 1
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
        'comment': order_data['comment'],
        'promo_code': order_data.get('promo_code', None)
    }

    orders.append(new_order)
    db["orders"] = orders
    save_db(db)

    ORDERS[:] = db["orders"]
    CUSTOMERS[:] = db["customers"]

    return new_order


def is_first_order(telegram_id):
    db = load_db()
    orders = db.get("orders", [])
    customer_orders = [order for order in orders if order.get('telegram_id') == telegram_id]
    return len(customer_orders) == 0


def get_order_by_id(order_id):
    db = load_db()
    orders = db.get("orders", [])
    return next((order for order in orders if order.get('id') == order_id), None)


def update_order(order_id, **kwargs):
    db = load_db()
    orders = db.get("orders", [])
    
    for order in orders:
        if order.get('id') == order_id:
            for key, value in kwargs.items():
                order[key] = value
            db["orders"] = orders
            save_db(db)
            ORDERS[:] = db["orders"]
            return order
    
    return None


def mark_order_paid(order_id):
    current_date = datetime.now().date().strftime('%d.%m.%Y')
    return update_order(order_id, status="Оплачен", start_date=current_date)