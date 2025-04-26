import logging

from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets import kbd


from coach_bot.dialogs.common.handlers.on_not_implemented import on_not_implemented
from coach_bot.dialogs.user_menu.getters import main_menu_getter
from coach_bot.services.coach_api import api_client
from coach_bot.states.user import UserMainMenu, Settings, Profile

logger = logging.getLogger(__name__)


# --- Handlers for button clicks ---
async def on_start_workout_clicked(
        callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager,
):
    await callback.answer("🏋️ Starting your workout! (Not implemented yet)")


async def on_progress_clicked(
        callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager,
):
    await callback.answer("📈 Showing your progress! (Not implemented yet)")


async def on_get_backup_codes_clicked(
    callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager,
):
    try:
        await manager.mark_closed()

        telegram_id = callback.from_user.id
        backup_codes = await api_client.get_backup_codes(telegram_id)

        codes_text = "\n".join(backup_codes)

        file_bytes = codes_text.encode("utf-8")
        document = types.BufferedInputFile(file_bytes, filename="backup_codes.txt")

        await callback.message.answer_document(
            document=document,
            caption=f"🔐 Ваши новые резервные коды:\n\n"
            f"<pre>{codes_text}\n</pre>\n"
            "‼️ Пожалуйста, сохраните их в безопасном месте.",
        )

        await callback.answer()

    except Exception as e:
        logger.exception("Failed to generate backup codes", exc_info=e)
        await callback.answer("❌ Ошибка при получении кодов.", show_alert=True)


async def on_edit_profile_clicked(
        callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager,
):
    await callback.answer("✏️ Editing profile! (Not implemented yet)")


# --- Dialogs ---
main_menu = Dialog(
    Window(
        Format("🏠 Добро пожаловать, {user_name}! Что вы хотите сделать?"),
        kbd.Row(
            kbd.Button(
                Const("🏋️ Начать тренировку"),
                id="start_workout",
                on_click=on_start_workout_clicked,
            ),
            kbd.Button(Const("📈 Прогресс"), id="progress", on_click=on_progress_clicked),
        ),
        kbd.Row(
            kbd.Button(Const("📋 Мой план"), id="my_plan", on_click=on_not_implemented),
            kbd.Button(Const("🎯 Моя цель"), id="my_goal", on_click=on_not_implemented),
        ),
        kbd.Row(
            kbd.Start(Const("⚙️ Настройки"), id="settings", state=Settings.menu),
        ),
        state=UserMainMenu.menu,
        getter=main_menu_getter,
    ),
)

settings_dialog = Dialog(
    Window(
        Const("⚙️ Настройки"),
        kbd.Row(
            kbd.Start(Const("👤 Профиль"), id="profile", state=Profile.show),
            kbd.Button(
                Const("🔐 Новые коды входа"),
                id="backup_codes",
                on_click=on_get_backup_codes_clicked,
            ),
        ),
        kbd.Row(
            kbd.Start(Const("⬅️ Назад в меню"), id="back_to_main", state=UserMainMenu.menu),
        ),
        state=Settings.menu,
    ),
)
