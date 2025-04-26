from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets import kbd
from aiogram_dialog.widgets.text import Const

from coach_bot.dialogs.common.handlers.on_not_implemented import on_not_implemented
from coach_bot.dialogs.common.widgets.profile_display import profile_text
from coach_bot.dialogs.user_menu.getters import get_user_profile
from coach_bot.services.coach_api import api_client
from coach_bot.states.user import Settings, Profile, ProfileForm


async def on_edit_profile_clicked(
    callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager,
):
    user_id = callback.from_user.id
    profile = await api_client.get_profile(user_id)

    await callback.answer()

    manager.dialog_data.update({
        "name": profile.name,
        "age": str(profile.age),
        "weight": str(profile.weight),
        "height": str(profile.height),
        "gender": profile.gender.value,
        "training_location": profile.training_location.value,
        "contraindications": set(profile.contraindications),
        "available_days": set(profile.available_days),
        "preferred_time": profile.preferred_time,
        "goal": str(profile.goal),
    })

    await manager.start(
        state=ProfileForm.name,
        mode=StartMode.RESET_STACK,
    )


profile_dialog = Dialog(
    Window(
        profile_text,
        kbd.Row(
            kbd.Button(
                Const("✏️ Изменить"),
                id="edit_profile",
                on_click=on_edit_profile_clicked,
            ),
            kbd.Start(
                Const("🔙 Назад"), id="back_to_settings", state=Settings.menu,
            ),
        ),
        kbd.Row(
            kbd.Button(Const("📤 Выйти"), id="logout", on_click=on_not_implemented),
        ),
        state=Profile.show,
        getter=get_user_profile,
    ),
)
