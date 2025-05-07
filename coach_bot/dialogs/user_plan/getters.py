from aiogram_dialog import DialogManager

from coach_bot.models.schemas import Plan
from coach_bot.services.coach_api import api_client


async def user_plan_getter(dialog_manager: DialogManager, **kwargs):
    plan: Plan = dialog_manager.dialog_data["plan"]

    start_date = plan.start_date
    end_date = plan.end_date
    progress = plan.progress_percent
    status = plan.status.value
    schedule = plan.schedule
    program_name = plan.program_name
    goal_name = plan.goal_name

    status_emojis = {
        "active": "🟢 Активный",
        "completed": "✅ Завершён",
        "cancelled": "❌ Отменён",
    }
    status_text = status_emojis.get(status, "❓ Неизвестный статус")

    progress_emoji = "🔥" if progress >= 50 else "🐢"

    total_days = len(schedule)

    plan_text = (
        f"📋 Ваш план тренировок:\n\n"
        f"📚 Программа: {program_name}\n"
        f"🎯 Цель: {goal_name}\n"
        f"📅 Начало: {start_date:%d.%m.%Y}\n"
        f"🏁 Конец: {end_date:%d.%m.%Y}\n"
        f"🗓️ Дней в расписании: {total_days}\n"
        f"{progress_emoji} Прогресс: {progress}%\n"
        f"🛠️ Статус: {status_text}\n"
    )

    return {"plan_text": plan_text}
