from aiogram import F, Router, types


router = Router()


@router.message(F.text == "Заказать торт")
