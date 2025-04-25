import logging
import types
from typing import Any

import httpx
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Start
from aiogram_dialog.widgets.text import Const, Format

from coach_bot.constants.messages import ErrorMessages, SettingsMessages, StartMessages
from coach_bot.handlers.user.backup_codes import on_get_backup_codes
from coach_bot.handlers.user.registration import on_edit_profile
from coach_bot.services.user_client import get_user
from coach_bot.states.menu import MainMenu, Profile, Settings

logger = logging.getLogger(__name__)


# ───────────────────────── getters ──────────────────────── #
async def main_getter(dialog_manager: DialogManager, **kwargs) -> dict[str]:
    tg_user = dialog_manager.event.from_user
    telegram_id = tg_user.id

    try:
        backend_user = await get_user(telegram_id)
        name = backend_user.name
    except httpx.RequestError as e:
        logger.error("Backend unavailable", exc_info=e)
        # send one‑time warning
        msg: types.Message = (
            dialog_manager.event.message
            if isinstance(dialog_manager.event, types.CallbackQuery)
            else dialog_manager.event
        )
        await msg.answer(ErrorMessages.backend_unavailable)
        # fallback to Telegram name
        name = tg_user.first_name or tg_user.username or "there"
    except Exception as e:
        logger.error("Error while fetching user", exc_info=e)
        name = tg_user.first_name or tg_user.username or "there"

    return {"name": name}


async def profile_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    user = await get_user(dialog_manager.event.from_user.id)
    if user:
        user_dict = user.model_dump()
        user_dict["preferred_time"] = user.preferred_time.strftime("%H:%M")
        user_dict["available_days"] = ", ".join(user.available_days)
        user_dict["training_location"] = user.training_location.value.title()

        return user_dict
    return {"": ""}


# ───────────────────────── windows ──────────────────────── #
main_menu = Dialog(
    Window(
        Format(StartMessages.welcome_registered),
        Row(
            Button(Const("🏋️ Начать тренировку"), id="workout"),
            Button(Const("📊 Прогресс"), id="progress"),
        ),
        Row(
            Start(Const("⚙️ Настройки"), id="settings", state=Settings.START),
        ),
        getter=main_getter,
        state=MainMenu.START,
    ),
)

settings_dialog = Dialog(
    Window(
        Const("⚙️ Настройки"),
        Row(
            Start(Const("👤 Профиль"), id="profile", state=Profile.SHOW),
            Button(
                Const("🔐 Получить новые резервные коды"),
                id="chg_codes",
                on_click=on_get_backup_codes,
            ),
        ),
        Row(Cancel(Const("◀️ Назад"))),
        state=Settings.START,
    ),
)

profile_dialog = Dialog(
    Window(
        Format(
            SettingsMessages.profile_view,
        ),
        Row(
            Button(
                Const("✏️ Изменить"),
                id="edit_profile",
                on_click=on_edit_profile,
            ),
            Cancel(Const("◀️ Назад")),
        ),
        state=Profile.SHOW,
        getter=profile_getter,
    ),
)
