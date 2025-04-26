from aiogram import Router
from aiogram.filters import CommandStart

from coach_bot.filters import ChatTypeFilter
from coach_bot.handlers.user import start


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())

    return user_router
