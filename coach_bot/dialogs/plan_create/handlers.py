from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from coach_bot.services.coach_api import api_client
from coach_bot.states.user import UserMainMenu


async def on_auto_generate(callback: CallbackQuery, button: Button, manager: DialogManager):
    telegram_id = callback.from_user.id
    await api_client.create_plan_auto(telegram_id)
    await callback.message.answer("✅ План успешно создан!")
    await manager.start(UserMainMenu.menu, mode=StartMode.RESET_STACK)


async def on_program_selected(callback: CallbackQuery, widget, manager: DialogManager, item_id: str):
    telegram_id = callback.from_user.id
    await api_client.create_plan_from_program(telegram_id, item_id)
    await callback.message.answer("✅ План успешно создан по выбранной программе!")
    await manager.start(UserMainMenu.menu, mode=StartMode.RESET_STACK)
