from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.input_file import FSInputFile
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    Message
)

from keyboards.ready_cake import *
from keyboards.menu import main_menu_kb
from handlers.states import OrderForm, CustomizationForm
from handlers.db_utils import *
from config import CAKES, CAKE_OPTIONS, IMG_PATH, PROMO_CODES
from decouple import config
import qrcode
import tempfile
import os
from urllib.parse import urlencode
from datetime import datetime


router = Router()


def get_option_by_id(options, option_id_str):
    try:
        option_id = int(option_id_str)
    except ValueError:
        return None
    
    for option in options:
        if option["id"] == option_id:
            return option
    return None


def generate_payment_url(order_id, amount, description):
    base_url = "https://paymaster.ru/payment/init"
    params = {
        "merchantId": config('PAYMENT_TOKEN'),
        "amount": str(amount),
        "currency": "RUB",
        "orderId": str(order_id),
        "description": description[:100],
        "testMode": "1",
    }
    return f"{base_url}?{urlencode(params)}"


def generate_qr_code_file(payment_url: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name, 'PNG')
    temp_file.close()
    
    return temp_file.name


@router.message(F.text == "Заказать торт")
async def start_order_cake(message: types.Message):  
    await message.answer(
        "Выберите торт из каталога:\n",
        reply_markup=generate_cake_kb()
    )


@router.callback_query(F.data.startswith("cake_"))
async def show_cake_details(callback: types.CallbackQuery):
    await callback.message.delete()
    cake_id = int(callback.data.split("_")[1])
    cake = next((c for c in CAKES if c["id"] == cake_id), None)

    image_path = IMG_PATH / cake["image"]

    cake_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить кастомизацию для торта", callback_data=f"customize_cake_{cake['id']}")],
        [InlineKeyboardButton(text="Заказать стандартный торт", callback_data=f"order_standard_{cake['id']}")],
        [InlineKeyboardButton(text="К списку тортов", callback_data="cakes_list")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ])

    cake_text = (
        f"{cake['name']}\n\n"
        f"{cake['description']}\n"
        f"{cake['weight']} - {cake['price']}₽"
    )

    try:
        photo = FSInputFile(image_path)
        await callback.message.answer_photo(
            photo=photo,
            caption=cake_text,
            reply_markup=cake_kb
        )
    except FileNotFoundError:
        await callback.message.answer(
            cake_text + "\n\nФото загрузится позже",
            reply_markup=cake_kb
        )

    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("order_standard_"))
async def order_standard_cake(callback: types.CallbackQuery, state: FSMContext):
    cake_id = int(callback.data.split("_")[2])
    cake = next((c for c in CAKES if c["id"] == cake_id), None)
    
    await state.update_data(
        selected_cake=cake, 
        total_price=cake["price"],
        customization=None
    )
    
    await callback.message.delete()
    await callback.message.answer(
        f"Вы выбрали стандартный торт:\n\n"
        f"{cake['name']}\n"
        f"{cake['description']}\n"
        f"{cake['weight']} - {cake['price']}₽\n\n"
        "Оформляем заказ...\n"
        "Укажите, пожалуйста, ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(OrderForm.waiting_name)
    await callback.answer()


@router.callback_query(F.data.startswith("customize_cake_"))
async def start_customization(callback: types.CallbackQuery, state: FSMContext):
    cake_id = int(callback.data.split("_")[2])
    cake = next((c for c in CAKES if c["id"] == cake_id), None)
    
    await state.update_data(selected_cake=cake, total_price=cake["price"])
    await state.set_state(CustomizationForm.waiting_levels)
    
    await callback.message.delete()
    await callback.message.answer(
        f"Начинаем кастомизацию торта - {cake['name']}!\n\n"
        "1. Выберите количество уровней:",
        reply_markup=generate_levels_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("level_"), CustomizationForm.waiting_levels)
async def select_level(callback: types.CallbackQuery, state: FSMContext):
    level_id = callback.data.split("_")[1]
    level = get_option_by_id(CAKE_OPTIONS["levels"], level_id)
    
    if not level:
        await callback.answer("Уровень не найден. Попробуйте выбрать заново.", show_alert=True)
        await callback.message.edit_text(
            "Выберите количество уровней:",
            reply_markup=generate_levels_kb()
        )
        return
    
    await state.update_data(levels=level)
    await state.set_state(CustomizationForm.waiting_shape)
    
    data = await state.get_data()
    new_price = data["total_price"] + level["price_add"]
    await state.update_data(total_price=new_price)
    
    await callback.message.edit_text(
        f"✓ {level['name']} (+{level['price_add']}₽)\n\n"
        "2. Выберите форму:",
        reply_markup=generate_shapes_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("shape_"), CustomizationForm.waiting_shape)
async def select_shape(callback: types.CallbackQuery, state: FSMContext):
    shape_id = callback.data.split("_")[1]
    shape = get_option_by_id(CAKE_OPTIONS["shapes"], shape_id)

    if not shape:
        await callback.answer("Форма не найдена.", show_alert=True)
        return
    
    await state.update_data(shape=shape)
    await state.set_state(CustomizationForm.waiting_topping)
    
    data = await state.get_data()
    new_price = data["total_price"] + shape["price_add"]
    await state.update_data(total_price=new_price)
    
    await callback.message.edit_text(
        f"✓ {data['levels']['name']}\n"
        f"✓ {shape['name']} (+{shape['price_add']}₽)\n\n"
        "3. Выберите топпинг:",
        reply_markup=generate_toppings_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topping_"), CustomizationForm.waiting_topping)
async def select_topping(callback: types.CallbackQuery, state: FSMContext):
    topping_id = callback.data.split("_")[1]
    topping = get_option_by_id(CAKE_OPTIONS["toppings"], topping_id)

    if not topping:
        await callback.answer("Топпинг не найден.", show_alert=True)
        return
    
    await state.update_data(topping=topping)
    await state.set_state(CustomizationForm.waiting_berries)
    
    data = await state.get_data()
    new_price = data["total_price"] + topping["price_add"]
    await state.update_data(total_price=new_price)
    
    await callback.message.edit_text(
        f"✓ {data['levels']['name']}\n"
        f"✓ {data['shape']['name']}\n"
        f"✓ {topping['name']} (+{topping['price_add']}₽)\n\n"
        "4. Ягоды (можно пропустить):",
        reply_markup=generate_berries_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith(("berry_", "berry_none")), CustomizationForm.waiting_berries)
async def select_berry(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if callback.data == "berry_none":
        await state.update_data(berries=None)
        await callback.message.edit_text(
            f"✓ {data['levels']['name']}\n"
            f"✓ {data['shape']['name']}\n"
            f"✓ {data['topping']['name']}\n"
            f"✗ Без ягод\n\n"
            "5. Декор (можно пропустить):",
            reply_markup=generate_decor_kb()
        )
    else:
        berry_id = callback.data.split("_")[1]
        berry = get_option_by_id(CAKE_OPTIONS["berries"], berry_id)
        
        if not berry:
            await callback.answer("Ягода не найдена!", show_alert=True)
            return
        
        await state.update_data(berries=berry)
        new_price = data["total_price"] + berry["price_add"]
        await state.update_data(total_price=new_price)
        
        await callback.message.edit_text(
            f"✓ {data['levels']['name']}\n"
            f"✓ {data['shape']['name']}\n"
            f"✓ {data['topping']['name']}\n"
            f"✓ {berry['name']} (+{berry['price_add']}₽)\n\n"
            "5. Декор (можно пропустить):",
            reply_markup=generate_decor_kb()
        )
    
    await state.set_state(CustomizationForm.waiting_decor)
    await callback.answer()


@router.callback_query(F.data.startswith(("decor_", "decor_none")), CustomizationForm.waiting_decor)
async def select_decor(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    finish_text = f"✓ {data['levels']['name']}\n✓ {data['shape']['name']}\n✓ {data['topping']['name']}\n"

    berries_text = f"✓ {data['berries']['name']}" if data.get('berries') else "Без ягод"
    finish_text += f"{berries_text}\n"

    if callback.data == "decor_none":
        await state.update_data(decor=None)
        finish_text += "✗ Без декора\n\n"
    else:
        decor_id = callback.data.split("_")[1]
        decor = get_option_by_id(CAKE_OPTIONS["decorations"], decor_id)

        if not decor:
            await callback.answer("Декор не найден!", show_alert=True)
            return

        new_price = data["total_price"] + decor["price_add"]
        await state.update_data(decor=decor, total_price=new_price)
        finish_text += f"✓ {decor['name']} (+{decor['price_add']}₽)\n\nТекущая цена: {new_price}₽\n\n"
    
    finish_text += "6. Надпись на торте:"
    
    await callback.message.edit_text(
        finish_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добавить надпись (+500₽)", callback_data="add_message")],
            [InlineKeyboardButton(text="Готово, оформить заказ", callback_data="customization_done")]
        ])
    )
    await state.set_state(CustomizationForm.waiting_message)
    await callback.answer()


@router.callback_query(F.data == "add_message", CustomizationForm.waiting_message)
async def add_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CustomizationForm.waiting_message)
    await callback.message.edit_text(
        "Введите текст надписи на торте (или нажмите «пропустить»):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="skip_message")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data.in_(["customization_done", "skip_message"]), CustomizationForm.waiting_message)
async def finish_customization(callback: types.CallbackQuery, state: FSMContext):
    await start_order_form(callback, state)


@router.message(CustomizationForm.waiting_message)
async def process_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.strip().lower() in ['пропустить', 'skip', 'нет', 'отмена']:
        await state.update_data(message=None)
        await start_order_form(message, state)
    else:
        new_price = data["total_price"] + 500
        await state.update_data(message=message.text.strip(), total_price=new_price)
        await start_order_form(message, state)


async def start_order_form(message_or_callback, state: FSMContext):
    data = await state.get_data()
    cake = data["selected_cake"]

    custom_parts = [data["levels"]["name"]]
    if data.get("shape"): 
        custom_parts.append(data["shape"]["name"])
    if data.get("topping") and data["topping"]["name"] != "Без топпинга": 
        custom_parts.append(data["topping"]["name"])
    if data.get("berries"): 
        custom_parts.append(data["berries"]["name"])
    else: 
        custom_parts.append("Без ягод")
    if data.get("decor"): 
        custom_parts.append(data["decor"]["name"])
    else: 
        custom_parts.append("Без декора")
    if data.get("message"): 
        custom_parts.append(f'Надпись: "{data["message"]}"')

    await state.update_data(customization=" | ".join(custom_parts))

    customization_text = data.get('customization', 'Кастомизация') or 'Стандартный'
    
    if isinstance(message_or_callback, types.CallbackQuery):
        await message_or_callback.message.delete()
        await message_or_callback.message.answer(
            f"Заказ: \n{cake['name']}\n{cake['weight']} - {data['total_price']}₽\n"
            f"Кастомизация: {customization_text}\n\n"
            f"Укажите ваше ФИО:",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message_or_callback.delete()
        await message_or_callback.answer(
            f"Заказ:\n{cake['name']}\n{cake['weight']} - {data['total_price']}₽\n"
            f"Кастомизация: {customization_text}\n\n"
            f"Укажите ваше ФИО:",
            reply_markup=ReplyKeyboardRemove()
        )
    
    await state.set_state(OrderForm.waiting_name)


@router.callback_query(F.data == "start_checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(OrderForm.waiting_name)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(
        "Введите, пожалуйста, ФИО:\n\n"
        "Сохраним для следующих заказов"
    )
    await callback.answer()


@router.message(OrderForm.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.waiting_phone)
    await message.answer(
        f"{message.text}\n\n"
        "Введите, пожалуйста, номер телефона вручную\n"
        "или отправьте его автоматически:",
        reply_markup=generate_request_contact_kb()
    )


@router.message(OrderForm.waiting_phone, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await process_phone_next(message, state, phone)


@router.message(OrderForm.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await process_phone_next(message, state, message.text)


async def process_phone_next(message: types.Message, state: FSMContext, phone: str):
    await state.set_state(OrderForm.waiting_address)
    user_id = message.from_user.id
    customer = None
    db = load_db()
    customers = db.get('customers', [])
    for client in customers:
        if str(client.get('telegram_id')) == str(user_id):
            customer = client
            break

    if customer:
        await message.answer(
            "Введите, пожалуйста, адрес или выберите ранее использованный:\n",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=customer['address'])]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
    else:
        await message.answer(
            "Введите, пожалуйста, адрес:\n",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(OrderForm.waiting_address, F.text != "Отмена повторного заказа")
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)

    await state.set_state(OrderForm.waiting_date)

    await message.answer(
        "Введите дату:\n"
        "В формате - 15.12.2025\n\n"
        "Срочная 24ч: +20%",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(OrderForm.waiting_date)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(OrderForm.waiting_time)
    await message.answer(
        "Выберете время\n"
        "`18:00` (12:00-21:00)",
        reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    )


@router.callback_query(F.data == "skip_comment", OrderForm.waiting_comment)
async def skip_comment_inline(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(comment="-")
    await state.set_state(OrderForm.waiting_summary)
    await show_order_summary(callback.message, state)
    await callback.answer("Комментарий пропущен!")


@router.message(OrderForm.waiting_time)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)

    data = await state.get_data()
    total_price = data["total_price"]
    
    today_str = datetime.now().strftime("%d.%m.%Y")
    if data["date"] == today_str:
        total_price = int(total_price * 1.2)
    
    await state.update_data(total_price=total_price)
    
    await message.answer(
        f"ИТОГО: {total_price}₽\n\n"
        f"Есть промокод?\n"
        "Введите промокод или кнопку «пропустить»:",
        reply_markup=get_promocode_kb()
    )
    await state.set_state(OrderForm.waiting_promo)


@router.message(OrderForm.waiting_promo)
async def process_promo(message: types.Message, state: FSMContext):
    promo_code = message.text.strip().upper()

    if promo_code.lower() == "нет":
        await state.update_data(promo_code=None, discount_percent=0)
        await next_step_after_promo(message, state) 
        return

    promo = get_valid_promo(promo_code)

    if promo:
        await state.update_data(promo_code=promo_code)
        data = await state.get_data()
        discount_percent = promo["discount_percent"]
        increase_promo_usage(promo_code)
        await message.answer(
            f"Поздравляем! Вы получили скидку {discount_percent}%",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.update_data(
            promo_code=promo_code, 
            discount_percent=discount_percent
        )
    else:
        await message.answer(
            "К сожалению, такого промокода не существует или он истёк.\n"
            "Попробуйте ещё раз или нажмите «Пропустить»:",
            reply_markup=get_promocode_kb()
        )
        return

    await next_step_after_promo(message, state)


async def next_step_after_promo(message_or_callback, state: FSMContext):
    await state.set_state(OrderForm.waiting_comment)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_comment")]
    ])
    
    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(
            "💬 Комментарий к заказу (можно пропустить):", 
            reply_markup=kb
        )
    else:  # CallbackQuery
        await message_or_callback.message.answer(
            "💬 Комментарий к заказу (можно пропустить):", 
            reply_markup=kb
        )


@router.callback_query(F.data == "skip_promocode", OrderForm.waiting_promo)
async def skip_promo_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(promo_code=None, discount_percent=0)
    await next_step_after_promo(callback.message, state)
    await callback.answer("Промокод пропущен")


@router.message(OrderForm.waiting_comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text or "-")
    await state.set_state(OrderForm.waiting_summary)
    await show_order_summary(message, state)


async def show_order_summary(message_or_callback, state: FSMContext):
    data = await state.get_data()
    cake = data["selected_cake"]

    final_price = data["total_price"]
    if data.get("discount_percent"):
        discount = int(data["total_price"] * data["discount_percent"] / 100)
        final_price -= discount

    summary = (
        f"Заказ готов!\n\n"
        f"{data['name']}\n"
        f"{data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"Дата: {data['date']} {data['time']}\n"
        f"Комментарий к заказу: {data.get('comment', '-')}\n\n"
        f"Торт: {cake['name']}\n"
        f"Итоговая стоимость: {final_price}₽"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить заказ", callback_data="order_confirmed")],
        [InlineKeyboardButton(text="Изменить", callback_data="restart_order")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ])

    if isinstance(message_or_callback, types.Message):
        try:
            await message_or_callback.delete()
        except:
            pass
        await message_or_callback.answer(summary, reply_markup=kb)
    else:
        await message_or_callback.message.edit_text(summary, reply_markup=kb)


@router.callback_query(F.data == "order_confirmed", OrderForm.waiting_summary)
async def processing_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cake = data['selected_cake']
    promo_code = data.get('promo_code')
    user_id = callback.from_user.id

    try:
        await callback.message.delete()
    except Exception as error:
        print(f'Ошибка при удалении сообщения: {error}')

    customer = create_or_find_customer(
        tg_id=user_id,
        name=data['name'],
        phone=data['phone'],
        address=data['address'])
    
    final_price = data["total_price"]
    discount_percent = data.get("discount_percent", 0)
    if discount_percent > 0:
        discount_amount = int(final_price * discount_percent / 100)
        final_price -= discount_amount
        if promo_code:
            increase_promo_usage(promo_code)

    order_data = {
        'name': data['name'],
        'customer_id': customer['id'],
        'phone_number': data['phone'],
        'product_id': cake['id'],
        'product_name': cake['name'],
        'total_price': final_price,
        'date': data['date'],
        'time': data['time'],
        'address': data['address'],
        'comment': data.get('comment', '-'),
        'customization': data.get('customization', '-'),
        'promo_code': promo_code
    }

    new_order = create_order(order_data)
    order_id = new_order['id']

    description = f"Торт {cake['name']} #{order_id}"
    payment_url = generate_payment_url(order_id, final_price, description)

    payment_kb = generate_payment_kb(order_id, payment_url)

    summary = (
        f"✅ Заказ #{order_id} успешно оформлен!\n\n"
        f"Детали заказа:\n"
        f"- Торт: {cake['name']}\n"
        f"- Стоимость: {new_order['total_price']}₽\n"
        f"- Комментарий: {new_order['comment']}\n"
        f"- Доставка: {new_order['deliver_to']}\n"
        f"- Адрес: {new_order['address']}\n"
        f"- Статус: {new_order['status']}\n\n"
    )

    if discount_percent > 0 and promo_code:
        summary += f"Промокод: {promo_code} (-{discount_percent}%)\n"

    summary += f"\nНомер заказа: #{order_id}\n\nДля продолжения нажмите «Оплатить»"

    await callback.message.answer(summary, reply_markup=payment_kb)

    manager_id = config('ADMIN_CHAT_ID', default=None)
    if manager_id:
        try:
            await callback.bot.send_message(
                manager_id,
                f"Новая заявка #{order_id}!\n\n{summary}"
            )
        except Exception:
            pass

    await state.update_data(current_order_id=order_id)
    await state.set_state(OrderForm.waiting_payment)
    await callback.answer("Заказ создан! Перейдите к оплате")


@router.callback_query(F.data.startswith("pay_order_"))
async def process_pay_order(callback: types.CallbackQuery, state: FSMContext):
    try: 
        order_id = int(callback.data.replace("pay_order_", ""))
        
        order = get_order_by_id(order_id)
        if not order:
            await callback.message.answer("Заказ не найден!")
            await callback.answer()
            return

        description = f"Торт - {order.get('product_name', 'Торт')} #{order_id}"
        payment_url = generate_payment_url(
            order_id=order_id,
            amount=order['total_price'],
            description=description
        )

        qr_file_path = generate_qr_code_file(payment_url)
        qr_image = FSInputFile(qr_file_path)
        
        await callback.message.answer_photo(
            photo=qr_image,
            caption=(
                f"СКАНИРУЙТЕ QR КОД ДЛЯ ОПЛАТЫ\n\n"
                f"Заказ: #{order_id}\n"
                f"Сумма: {order['total_price']} ₽\n\n"
                f"{description}\n\n"
                f"Сохраните номер заказа #{order_id}!"
            ),
            reply_markup=generate_payment_kb(order_id, payment_url)
        )

        try:
            os.unlink(qr_file_path)
        except:
            pass

        await callback.answer("QR-код отправлен! Сканируйте для оплаты")

    except Exception as e:
        print(f"Traceback: {e}")

        order_id = int(callback.data.replace("pay_order_", ""))
        order = get_order_by_id(order_id)
        if order:
            payment_url = generate_payment_url(order_id, order['total_price'], "Торт")
            await callback.message.answer(
                f"ОПЛАТА ПО ССЫЛКЕ (QR временно недоступен)\n\n"
                f"Заказ #{order_id} - {order['total_price']}₽\n\n"
                f"[Перейти к оплате]({payment_url})",
                reply_markup=generate_payment_kb(order_id, payment_url),
                disable_web_page_preview=True
            )
        await callback.answer("Ссылка на оплату отправлена!")


@router.callback_query(F.data.startswith("check_payment_"))
async def process_check_payment(callback: types.CallbackQuery, state: FSMContext):
    order_id = int(callback.data.replace("check_payment_", ""))
    
    order = get_order_by_id(order_id)
    
    if not order:
        await callback.message.answer("Заказ не найден")
        await callback.answer()
        return

    current_date = datetime.now().date()

    update_order(order_id, status="Оплачен", start_date=current_date.strftime('%d.%m.%Y'))
    mark_order_paid(order_id)

    order = get_order_by_id(order_id)
    
    success_text = (
        f"Оплата прошла успешно!\n\n"
        f"Заказ: #{order_id}\n"
        f"Торт: {order.get('product_name')}\n"
        f"Доставка: {order.get('deliver_to')}\n"
        f"Адрес: {order.get('address')}\n"
        f"Сумма: {order.get('total_price')} ₽\n"
        f"Статус: Оплачен"
    )

    await callback.message.answer(
        success_text, 
        reply_markup=generate_payment_success_kb(order_id)
    )
    await callback.answer("Оплата подтверждена!")


@router.callback_query(F.data == "cakes_list")
async def back_to_cakes_list(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Выберите торт из каталога:",
        reply_markup=generate_cake_kb()
    )
    await callback.answer("К списку тортов")


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Вы перешли на главное меню",
        reply_markup=main_menu_kb(callback.from_user.id)
    )
    await callback.answer()


@router.callback_query(F.data == "restart_order")
async def restart_order(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Заказ отменен. Начните заново:",
        reply_markup=generate_cake_kb()
    )
    await callback.answer("Заказ сброшен")


@router.callback_query(F.data == "cancel_custom")
async def cancel_customization(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Кастомизация отменена.\nВыберите торт из каталога:",
        reply_markup=generate_cake_kb()
    )
    await callback.answer("Кастомизация отменена")