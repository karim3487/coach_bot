from aiogram_dialog import DialogManager

from coach_bot.models.schemas import Progress
from coach_bot.services.coach_api import api_client


async def progress_getter(dialog_manager: DialogManager, **kwargs):
    telegram_id = dialog_manager.event.from_user.id
    current_page = dialog_manager.dialog_data.get("page", 1)

    response = await api_client.get_progress(telegram_id)
    dialog_manager.dialog_data["page"] = current_page
    dialog_manager.dialog_data["total_pages"] = response.total_pages

    if not response.results:
        return {"text": "📅 Пока нет прогресса."}

    def format_entry(entry: Progress) -> str:
        date = entry.date.strftime("%d.%m.%Y")
        return (
            f"📅 <b>{date}</b> — "
            f"{entry.metric}: <b>{entry.value} {entry.units}</b> "
            f"{f'({entry.exercise_name})' if entry.exercise else ''}"
        )

    formatted_progress = "\n".join(format_entry(e) for e in response.results)
    return {
        "progress_text": formatted_progress or "Нет данных о прогрессе.",
        "current_page": current_page,
        "total_pages": response.total_pages or 1,
    }
