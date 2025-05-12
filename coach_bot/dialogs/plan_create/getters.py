from slugify import slugify
from coach_bot.services.coach_api import api_client


async def programs_getter(dialog_manager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    current_page = dialog_manager.dialog_data.get("page", 1)

    profile = await api_client.get_profile(user_id)
    response = await api_client.get_programs(profile.goal.id, profile.training_location.value, page=current_page)
    dialog_manager.dialog_data["page"] = current_page
    dialog_manager.dialog_data["total_pages"] = response.total_pages

    programs = response.results

    programs_description = "\n\n".join(
        f"{idx + 1}. {program.name} — {program.days_per_week} раз в неделю\n{program.description}"
        for idx, program in enumerate(programs)
    )

    program_buttons = [{"id": p.id, "item_number": str(idx + 1)} for idx, p in enumerate(programs)]

    return {
        "program_buttons": program_buttons,
        "programs_description": programs_description,
        "current_page": response.current_page,
        "total_pages": response.total_pages,
    }
