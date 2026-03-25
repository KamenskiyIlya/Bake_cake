from aiogram import F, Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from keyboards.ready_cake import generate_cake_kb
from keyboards.menu import main_menu_kb
from config import CAKES, IMG_PATH


router = Router()


@router.message(F.text == "Посмотреть готовый торт")
async def start_order_cake(message: types.Message):  
    await message.answer(
        "Выберите торт из каталога:\n",
        reply_markup=generate_cake_kb(),
        parse_mode="Markdown"
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
            reply_markup=cake_kb,
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        await callback.message.answer(
            cake_text + "\n\nФото загрузится позже",
            reply_markup=cake_kb,
            parse_mode="Markdown"
        )

    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == "cakes_list")
async def back_to_cakes_list(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Выберите торт из каталога:",
        reply_markup=generate_cake_kb(),
        parse_mode="Markdown"
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