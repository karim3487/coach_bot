from aiogram_dialog import DialogManager

from coach_bot.services.coach_api import api_client
from coach_bot.utils.utils import format_datetime


async def schedule_getter(dialog_manager: DialogManager, **kwargs):
    telegram_id = dialog_manager.event.from_user.id
    current_page = dialog_manager.dialog_data.get("page", 1)

    response = await api_client.get_schedule(telegram_id, current_page)
    dialog_manager.dialog_data["page"] = current_page
    dialog_manager.dialog_data["total_pages"] = response.total_pages

    if not response.results:
        return {"schedule_text": "📅 Пока нет запланированных тренировок."}

    lines = []
    for item in response.results:
        status = "✅" if item.completed else "🕒"
        formatted = format_datetime(item.date, item.time)
        workout_name = item.workout_name or "Без названия"
        lines.append(f"{status} {formatted} — {workout_name}")

    return {
        "schedule_text": "\n".join(lines),
        "current_page": current_page,
        "total_pages": response.total_pages or 1,
    }
