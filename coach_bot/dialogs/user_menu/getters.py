from aiogram_dialog import DialogManager

from coach_bot.dialogs.common.utils import get_display_name, get_display_list
from coach_bot.services.coach_api import api_client
from coach_bot.utils.constants import DAYS_OF_WEEK, GENDERS, LOCATIONS, CONTRAINDICATIONS


async def main_menu_getter(dialog_manager: DialogManager, **kwargs):
    telegram_id = dialog_manager.event.from_user.id
    profile = await api_client.get_profile(telegram_id)

    return {
        "user_name": profile.name if profile else "Атлет",
    }


async def get_user_profile(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    profile = await api_client.get_profile(user_id)

    return {
        "name": profile.name,
        "age": profile.age,
        "weight": profile.weight,
        "height": profile.height,
        "gender": get_display_name(GENDERS, profile.gender.value),
        "training_location": get_display_name(LOCATIONS, profile.training_location.value),
        "contraindications": get_display_list(CONTRAINDICATIONS, profile.contraindications),
        "available_days": ", ".join(get_display_list(DAYS_OF_WEEK, profile.available_days)),
        "preferred_time": profile.preferred_time,
        "goal_display": profile.goal,
        "user_name": profile.name,
    }
