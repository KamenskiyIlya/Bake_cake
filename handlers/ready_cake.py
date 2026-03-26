from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.input_file import FSInputFile
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from keyboards.ready_cake import *
from keyboards.menu import main_menu_kb
from config import CAKES, CAKE_OPTIONS, IMG_PATH
from datetime import datetime


router = Router()


class OrderForm(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()
    waiting_date = State()
    waiting_time = State()
    waiting_comment = State()


class CustomizationForm(StatesGroup):
    waiting_levels = State()
    waiting_shape = State()
    waiting_topping = State()
    waiting_berries = State()
    waiting_decor = State()
    waiting_message = State()


def get_option_by_id(options, option_id_str):
    try:
        option_id = int(option_id_str)
    except ValueError:
        return None
    
    for option in options:
        if option["id"] == option_id:
            return option
    return None


@router.message(F.text == "Заказать торт")
async def start_order_cake(message: types.Message):  
    await message.answer(
        "Выберите торт из каталога:\n",
        reply_markup=generate_cake_kb()
    )


@router.callback_query(F.data.startswith("cake_"))
async def show_cake_details(callback: types.CallbackQuery):
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

    berries_text = f"✓ {data['berries']['name']}" if data.get('berries') else "✗ Без ягод"
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
        "Введите текст надписи на торте (или отправьте «пропустить»):",
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
        await start_order_form(message, state)
    else:
        await state.update_data(message=message.text.strip(), total_price=data["total_price"] + 500)
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
    await message.answer(
        "Введите, пожалуйста, адрес:\n",
        reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    )


@router.message(OrderForm.waiting_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderForm.waiting_date)
    await message.answer(
        "Введите дату:\n"
        "В формате - 15.12.2025\n\n"
        "Срочная 24ч: +20%",
        reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
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
    try:
        await callback.message.delete()
    except:
        pass
    await show_order_summary(callback.message, state)
    await callback.answer("Комментарий пропущен!")


@router.message(OrderForm.waiting_comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    try:
        await message.delete()
    except:
        pass
    await show_order_summary(message, state)


@router.message(OrderForm.waiting_time)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(OrderForm.waiting_comment)

    data = await state.get_data()
    cake = data["selected_cake"]
    total_price = cake["price"]
    
    today_str = datetime.now().strftime("%d.%m.%Y")
    if data["date"] == today_str:
        total_price = int(total_price * 1.2)
    
    await state.update_data(total_price=total_price)
    
    await message.answer(
        f"ИТОГО: {total_price}₽\n\n"
        "Комментарий к заказу?\n",
        reply_markup=generate_skip_comment_kb()
    )


async def show_order_summary(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cake = data["selected_cake"]
    
    summary = (
        f"Заказ готов!\n\n"
        f"{data['name']}\n"
        f"{data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"Дата: {data['date']} {data['time']}\n"
        f"Комментарий к заказу: {data['comment']}\n\n"
        f"Торт: {cake['name']}\n"
        f"Итоговая стоимость: {data['total_price']}₽"
    )
    
    await message.answer(
        summary,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить заказ", callback_data="order_confirmed")],
            [InlineKeyboardButton(text="Изменить", callback_data="restart_order")],
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
        ])
    )


@router.callback_query(F.data == "cakes_list")
async def back_to_cakes_list(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Выберите торт из каталога:",
        reply_markup=generate_cake_kb()
    )
    await callback.answer("К списку тортов")


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Вы перешли на главное меню",
        reply_markup=main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_custom")
async def cancel_customization(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Кастомизация отменена.\nВыберите торт из каталога:",
        reply_markup=generate_cake_kb()
    )
    await callback.answer("Кастомизация отменена")