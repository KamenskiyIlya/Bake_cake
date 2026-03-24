from aiogram import Dispatcher
from handlers.start import router as start_router


def register_routes(dp: Dispatcher):
    dp.include_router(start_router)