import logging
from functools import partial
from typing import Any

from aiogram import types
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets import kbd
from aiogram_dialog.widgets.text import Const, Format
from pydantic import ValidationError

from coach_bot.dialogs.common.widgets.buttons import back_button
from coach_bot.dialogs.common.widgets.profile_display import profile_text
from coach_bot.dialogs.profile_form.getters import goal_getter, get_profile_form_data
from coach_bot.dialogs.profile_form.handlers.checkbox_handlers import (
    on_contraindication_changed,
    on_contraindication_next,
    on_day_changed,
    on_days_next,
)
from coach_bot.dialogs.profile_form.handlers.input_handlers import on_text_input, selection_handler
from coach_bot.dialogs.profile_form.handlers.utils import build_checkbox_group
from coach_bot.models.schemas import ClientProfileCreate
from coach_bot.states.user import ProfileForm, UserMainMenu
from coach_bot.services.coach_api import api_client
from coach_bot.utils import constants

logger = logging.getLogger(__name__)

contraindications_group = build_checkbox_group(
    constants.CONTRAINDICATIONS, on_change_handler=on_contraindication_changed,
)
days_selection_group = build_checkbox_group(
    constants.DAYS_OF_WEEK, on_change_handler=on_day_changed,
)


async def on_finish(
        callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager,
):
    try:
        user = create_user_from_dialog_data(callback.from_user.id, manager.dialog_data)
        await api_client.create_or_update_user(user=user)
    except ValidationError as ve:
        await callback.message.answer("❌ Invalid data:\n" + str(ve))
        logger.warning(f"Validation failed: {ve}")
        return
    except Exception as e:
        logger.exception("Failed to create profile", exc_info=e)
        await callback.message.answer("❌ Error during profile creation.")
        return

    await manager.start(
        state=UserMainMenu.menu,
        mode=StartMode.RESET_STACK,
    )


def create_user_from_dialog_data(
        telegram_id: int, data: dict[str, Any],
) -> ClientProfileCreate:
    return ClientProfileCreate(
        telegram_id=telegram_id,
        goal=int(data["goal"]),
        name=data["name"],
        age=int(data["age"]),
        weight=str(data["weight"]),
        height=str(data["height"]),
        gender=data["gender"],
        contraindications=data.get("contraindications", []),
        training_location=data["training_location"],
        available_days=data.get("available_days", []),
        preferred_time=data["preferred_time"],
    )


profile_form_dialog = Dialog(
    Window(
        Const("📝 Введите ваше имя:"),
        MessageInput(partial(on_text_input, field="name")),
        state=ProfileForm.name,
    ),
    Window(
        Const("🎂 Укажите ваш возраст:"),
        MessageInput(partial(on_text_input, field="age")),
        state=ProfileForm.age,
    ),
    Window(
        Const("⚖️ Укажите ваш вес (в кг):"),
        MessageInput(partial(on_text_input, field="weight")),
        state=ProfileForm.weight,
    ),
    Window(
        Const("📏 Укажите ваш рост (в см):"),
        MessageInput(partial(on_text_input, field="height")),
        state=ProfileForm.height,
    ),
    Window(
        Const("🚻 Выберите ваш пол:"),
        kbd.Select(
            Format("{item[1]}"),
            items=constants.GENDERS,
            item_id_getter=lambda x: x[0],
            id="gender",
            on_click=selection_handler("gender"),
        ),
        state=ProfileForm.gender,
    ),
    Window(
        Const("🏟️ Где вы хотите тренироваться?"),
        kbd.Column(
            kbd.Select(
                Format("{item[1]}"),
                items=constants.LOCATIONS,
                item_id_getter=lambda x: x[0],
                id="training_location",
                on_click=selection_handler("training_location"),
            ),
        ),
        state=ProfileForm.training_location,
    ),
    Window(
        Const("⚕️ Есть ли у вас противопоказания?"),
        contraindications_group,
        kbd.Button(
            Const("➡️ Далее"),
            id="next_contraindications",
            on_click=on_contraindication_next,
        ),
        state=ProfileForm.contraindications,
    ),
    Window(
        Const("📅 Выберите дни, когда вам удобно заниматься:"),
        days_selection_group,
        kbd.Button(
            Const("➡️ Далее"),
            id="next_days",
            on_click=on_days_next,
        ),
        state=ProfileForm.available_days,
    ),
    Window(
        Const("⏰ Введите желаемое время тренировок (чч:мм):"),
        MessageInput(partial(on_text_input, field="preferred_time")),
        state=ProfileForm.preferred_time,
    ),
    Window(
        Const("🥥 Выберите вашу цель:"),
        kbd.Column(
            kbd.Select(
                Format("{item[name]}"),
                items="goals",
                item_id_getter=lambda x: str(x["id"]),
                id="goal",
                on_click=selection_handler("goal"),
            ),
        ),
        state=ProfileForm.goal,
        getter=goal_getter,
    ),
    Window(
        profile_text,
        kbd.Row(
            back_button,
            kbd.SwitchTo(Const("🔁 Изменить"), id="restart", state=ProfileForm.name),
        ),
        kbd.Row(
            kbd.Button(Const("✅ Подтвердить"), id="confirm", on_click=on_finish),
        ),
        state=ProfileForm.confirm,
        getter=get_profile_form_data,
    ),
)
