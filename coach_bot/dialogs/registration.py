# dialogs/registration.py

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Cancel, Next
from aiogram.types import Message
from aiogram_dialog import DialogManager
from coach_bot.states.user import ProfileForm


# Simple one-step registration for demo
async def on_name_entered(message: Message, widget: TextInput, dialog_manager: DialogManager, name: str):
    dialog_manager.dialog_data["name"] = name
    # telegram_id = message.from_user.id
    # # Minimal data for upsert
    # payload = {
    #     "telegram_id": telegram_id,
    #     "name": name,
    #     "age": 30,
    #     "weight": "70",
    #     "height": "175",
    #     "gender": "male",
    #     "training_location": "gym",
    #     "available_days": ["mon", "wed", "fri"],
    #     "preferred_time": "18:00:00",
    #     "contraindications": "none",
    #     "goal": 3,
    # }
    # profile = ClientProfileCreate(**payload)
    # await api_client.create_or_update_user(profile)
    # await dialog_manager.start(UserMainMenu.menu, mode=StartMode.RESET_STACK)


async def profile_form_getter(dialog_manager: DialogManager, **kwargs):
    # Optional pre-filled values
    # profile = dialog_manager.start_data.get("profile", {})
    profile = dialog_manager.dialog_data.get("profile", {})
    return {
        "name": profile.get("name", ""),
    }


profile_form_dialog = Dialog(
    Window(
        Format("📝 Let's set up your profile.\n\nYour name (current: {name}):"),
        TextInput(id="name_input", on_success=on_name_entered),
        Next(Const("➡️ Next")),
        Cancel(Const("❌ Cancel")),
        state=ProfileForm.name,
    ),
    getter=profile_form_getter,
)
