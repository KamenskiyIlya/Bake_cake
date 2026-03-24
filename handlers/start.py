from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from config import PD_PDF_PATH
from keyboards.menu import main_menu_kb


router = Router()


@router.message(Command("start"))
async def start_bot(message: types.Message):
    pdf = FSInputFile(PD_PDF_PATH)

    await message.answer_document(
        document=pdf,
        caption=(
            "Перед началом работы с ботом ознакомьтесь, пожалуйста, "
            "с согласием на обработку персональных данных."
        )
    )

    await message.answer(
        f"{message.from_user.full_name}, добро пожаловать в магазин тортов \"BakeCake\"!\n"
        "Мы создаём вкусные и красивые торты для любого праздника:\n"
        "- Свадьбы и юбилеи\n"
        "- Дни рождения и корпоративы\n"  
        "- Детские утренники\n\n"
        "Что мы предлагаем:\n"
        "- Готовые хиты из меню\n"
        "- Индивидуальные торты - соберите свой вкус\n"
        "Удивите гостей идеальным десертом! Просто выберите торт или создайте свой - и мы доставим вовремя.",
        reply_markup=main_menu_kb()
    )