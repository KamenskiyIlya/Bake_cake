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
from keyboards.ready_cake import generate_cake_kb, generate_request_contact_kb, generate_skip_comment_kb
from keyboards.menu import main_menu_kb
from config import CAKES, IMG_PATH
from datetime import datetime


router = Router()


class OrderForm(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()
    waiting_date = State()
    waiting_time = State()
    waiting_comment = State()


@router.message(F.text == "Посмотреть готовый торт")
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
        [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_cake_{cake['id']}")],
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


@router.callback_query(F.data.startswith("add_cake_"))
async def add_cake_to_cart(callback: types.CallbackQuery, state: FSMContext):
    cake_id = int(callback.data.split("_")[2])
    cake = next((c for c in CAKES if c["id"] == cake_id), None)

    await state.update_data(selected_cake=cake)
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        f"{cake['name']} в корзине!\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оформить", callback_data="start_checkout")],
            [InlineKeyboardButton(text="К тортам", callback_data="cakes_list")]
        ])
    )
    await callback.answer("Добавлено!")


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
        "В формате - 15.12.2025`\n\n"
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