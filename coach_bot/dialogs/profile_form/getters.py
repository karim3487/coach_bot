from aiogram_dialog import DialogManager

from coach_bot.dialogs.common.utils import get_display_name, get_display_list
from coach_bot.services.coach_api import api_client
from coach_bot.utils.constants import GENDERS, LOCATIONS, DAYS_OF_WEEK


async def goal_getter(dialog_manager: DialogManager, **kwargs):
    goals = await api_client.get_goals()
    return {"goals": [goal.dict() for goal in goals]}

async def get_profile_form_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    goal_display = await api_client.get_goal(data["goal"])

    return {
        "name": data.get("name", ""),
        "age": data.get("age", ""),
        "weight": data.get("weight", ""),
        "height": data.get("height", ""),
        "gender": get_display_name(GENDERS, data.get("gender", "")),
        "training_location": get_display_name(LOCATIONS, data.get("training_location")),
        "available_days": ", ".join(get_display_list(DAYS_OF_WEEK, list(data.get("available_days", [])))),
        "preferred_time": data.get("preferred_time", ""),
        "goal_id": data.get("goal", ""),
        "goal_display": goal_display.name,
    }
