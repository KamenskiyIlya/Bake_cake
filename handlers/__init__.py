from aiogram import Dispatcher
from handlers.start import router as start_router
from handlers.ready_cake import router as ready_cake_router


def register_routes(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(ready_cake_router)