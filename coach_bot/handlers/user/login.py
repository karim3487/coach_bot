import logging
from http.client import HTTPException

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode

from coach_bot.constants.messages import LoginMessages
from coach_bot.services.user_client import auth_with_backup_code
from coach_bot.states.login import LoginState
from coach_bot.states.menu import MainMenu

logger = logging.getLogger(__name__)


async def ask_login_code(message: types.Message, state: FSMContext) -> None:
    await message.answer(LoginMessages.ask_code)
    await state.set_state(LoginState.code)


async def submit_login_code(
    message: types.Message, state: FSMContext, dialog_manager: DialogManager
) -> None:
    telegram_id = str(message.from_user.id)
    code = message.text.strip()

    try:
        user = await auth_with_backup_code(code, telegram_id)
    except HTTPException as e:
        logger.warning(e)
        await message.answer(LoginMessages.invalid_code)
        return

    await message.answer(
        LoginMessages.welcome(user.full_name),
    )
    await state.clear()
    await dialog_manager.start(MainMenu.START, mode=StartMode.RESET_STACK)
    return
