import logging
from aiogram import types
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets import kbd

from coach_bot.services.coach_api import api_client
from coach_bot.states.user import PlanCreateMenu, UserPlanMenu

logger = logging.getLogger(__name__)


async def on_start_workout_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    await callback.answer("🏋️ Начать тренировку! (пока не реализовано)")


async def on_progress_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    await callback.answer("📈 Ваш прогресс! (пока не реализовано)")


async def on_my_plan_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    telegram_id = callback.from_user.id
    try:
        plan = await api_client.get_current_plan(telegram_id)
        if not plan:
            await callback.answer("📋 У вас нет активного плана. Давайте создадим!", show_alert=True)
            await manager.start(PlanCreateMenu.start, mode=StartMode.RESET_STACK)
        else:
            await manager.start(UserPlanMenu.menu, mode=StartMode.RESET_STACK)
    except Exception as e:
        logger.exception("Failed to check user plan", exc_info=e)
        await callback.answer("❌ Ошибка при проверке плана. Попробуйте позже.", show_alert=True)
