from aiogram import types
from aiogram_dialog import StartMode, DialogManager

from coach_bot.services.coach_api import api_client
from coach_bot.states.user import Guest, UserMainMenu


async def start(message: types.Message, dialog_manager: DialogManager) -> None:
    telegram_id = message.from_user.id

    profile = await api_client.get_profile(telegram_id)

    if profile:
        await dialog_manager.start(UserMainMenu.menu, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(Guest.menu, mode=StartMode.RESET_STACK)
