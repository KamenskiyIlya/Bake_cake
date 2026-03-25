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
        f'{message.from_user.full_name}, добро пожаловать в BakeCake! 🎂\n\n'
        'Мы — пекарня тортов на заказ, где каждый десерт создаётся с любовью и вниманием к деталям.\n\n'
        'У нас вы можете:\n'
        '- Заказать готовый торт из нашего ассортимента\n'
        '- Собрать свой уникальный торт — выбрать форму, начинку, декор и даже добавить персональную надпись\n'
        '- Подготовить идеальный десерт для любого повода: дня рождения, свадьбы или просто хорошего настроения\n\n'
        'Мы верим, что торт — это не просто десерт, а эмоции, которые остаются с вами и вашими близкими.\n\n'
        '🚚 Сроки доставки:\n'
        '• Доставка в течение 24 часов с момента заказа\n'
        '• Возможна срочная доставка (в день заказа) +20% к стоимости\n'
        '• Доступные интервалы: с 10:00 до 22:00\n'
        '• Вы всегда можете указать удобное время и комментарий для курьера\n\n'
        '👇 Начните с выбора: посмотреть готовые торты или собрать свой уникальный десерт!',
        reply_markup=main_menu_kb()
    )