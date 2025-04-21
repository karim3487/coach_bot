import logging

from aiogram import types
from aiogram_dialog import DialogManager

from coach_bot import states
from coach_bot.constants.messages import ErrorMessages, StartMessages
from coach_bot.keyboards.default.menu import MainMenuButtons
from coach_bot.services.user_client import get_user

logger = logging.getLogger(__name__)


async def start(message: types.Message, dialog_manager: DialogManager) -> None:
    telegram_id = message.from_user.id
    try:
        user = await get_user(telegram_id)
    except Exception as e:
        logger.exception("Ошибка при проверке авторизации", exc_info=e)
        await message.answer(ErrorMessages.backend_unavailable)
        return

    if user:
        await dialog_manager.start(states.menu.MainMenu.START)

    else:
        await message.answer(
            StartMessages.welcome_unregistered,
            reply_markup=MainMenuButtons.main_menu(),
        )
        return
    return
