import logging
from aiogram import types
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets import kbd

from coach_bot.models.schemas import Workout, ScheduleDetail
from coach_bot.services.coach_api import api_client
from coach_bot.states.user import PlanCreateMenu, UserPlanMenu, UserWorkout, UserProgress

logger = logging.getLogger(__name__)


async def on_start_workout_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    telegram_id = callback.from_user.id

    try:
        profile = await api_client.get_profile(telegram_id)
        if not profile:
            await callback.answer("❌ Профиль не найден.")
            return

        schedule: ScheduleDetail = await api_client.get_today_schedule(telegram_id)
        if not schedule or not schedule.workout:
            await manager.start(UserWorkout.no_workout)
            return

        if schedule.completed:
            await manager.mark_closed()
            completed_time = schedule.completed_at.strftime("%H:%M") if schedule.completed_at else "время неизвестно"
            await callback.answer(f"✅ Сегодняшняя тренировка уже завершена в {completed_time}.", show_alert=True)
            return

        workout: Workout = schedule.workout

        await manager.start(UserWorkout.overview, mode=StartMode.RESET_STACK, data={"workout": workout})

    except Exception as e:
        logger.exception("Ошибка при загрузке тренировки", exc_info=e)
        await callback.answer("❌ Ошибка при загрузке тренировки", show_alert=True)


async def on_progress_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    telegram_id = callback.from_user.id
    try:
        response = await api_client.get_progress(telegram_id, page=1)
        if len(response.results) <= 0:
            await callback.answer("❌ Пока нет записей о прогрессе.", show_alert=True)
            return
        manager.dialog_data["page"] = 1
        await manager.start(UserProgress.menu, mode=StartMode.RESET_STACK)
    except Exception as e:
        logger.exception("Error when progress loaded", exc_info=e)
        await callback.answer("❌ Не удалось загрузить прогресс", show_alert=True)


async def on_my_plan_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    telegram_id = callback.from_user.id
    try:
        plan = await api_client.get_current_plan(telegram_id)
        if not plan:
            await manager.start(PlanCreateMenu.start, mode=StartMode.RESET_STACK, data={"page": 1})
        else:
            await manager.start(UserPlanMenu.menu, mode=StartMode.RESET_STACK, data={"plan": plan})
    except Exception as e:
        logger.exception("Failed to check user plan", exc_info=e)
        await callback.answer("❌ Ошибка при проверке плана. Попробуйте позже.", show_alert=True)


async def on_goal_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    try:
        telegram_id = callback.from_user.id
        profile = await api_client.get_profile(telegram_id)

        if not profile or not profile.goal:
            await callback.answer("❌ Цель не указана.", show_alert=True)
            return
        goal = profile.goal
        description = goal.description if goal.description != "" else "Нет описания"
        await callback.message.answer(
            f"🎯 <b>Ваша цель:</b> {goal.name}\n"
            f"<b>Описание:</b> {description}",
            parse_mode="HTML",
        )
        await callback.answer()

    except Exception:
        await callback.answer("❌ Ошибка при загрузке цели", show_alert=True)
