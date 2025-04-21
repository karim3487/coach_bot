import logging
from typing import Any

import httpx
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from pydantic import ValidationError

from coach_bot.constants.messages import (
    BackupCodeMessages,
    RegistrationMessages,
    SettingsMessages,
)
from coach_bot.keyboards.default.registration import RegistrationButtons
from coach_bot.keyboards.inline.callbacks import ToggleDayCallback
from coach_bot.keyboards.inline.user.weekly import make_training_days_keyboard
from coach_bot.models.schemas import UserCreate, UserRead
from coach_bot.services.user_client import (
    create_or_update_user,
    get_backup_codes,
    get_user,
)
from coach_bot.states.menu import MainMenu
from coach_bot.states.registration import RegistrationState
from coach_bot.utils.parse_time import parse_time

logger = logging.getLogger(__name__)


def validate_age(age: int) -> None:
    if not (10 <= age <= 100):  # noqa: PLR2004
        raise ValueError(RegistrationMessages.invalid_age)


def format_question(label: str, current_value: Any | None, *, edit_mode: bool) -> str:
    """
    Add current value hint if we are editing.
    Returns:
        str: Formatted question string.
    """
    if edit_mode and current_value is not None:
        return (
            f"{label}\n\n"
            f"<b>Текущее значение:</b> {current_value}\n"
            f"Введите новое или нажмите «⏭️Оставить текущее»"
        )
    return label


def is_skip(msg: Message) -> bool:
    return msg.text == "⏭️Оставить текущее"


# --------------------------------------------------------------------------- #
# start                                                                       #
# --------------------------------------------------------------------------- #


async def on_edit_profile(
    c: types.CallbackQuery,
    _btn: Button,
    manager: DialogManager,
) -> None:
    # 1) закрываем текущий диалог (профиль / меню)
    await manager.reset_stack()
    # 2) получаем FSMContext, лежит в middleware_data
    state = manager.middleware_data["state"]
    # 3) запускаем анкету в режиме редактирования
    await start_registration(c.message, state, edit_mode=True)


async def on_edit(
    c: types.CallbackQuery,
    _b: Button,
    manager: DialogManager,
) -> None:
    await manager.done()  # закрываем Menu‑dialog
    # запускаем FSM‑анкету
    await start_registration(
        c.message, manager.middleware_data["state"], edit_mode=True
    )


async def start_registration(
    message: Message,
    state: FSMContext,
    *,  # only‑keyword
    edit_mode: bool = False,  # False → новая анкета  |  True → редактирование
) -> None:
    """Запуск анкеты регистрации / редактирования профиля."""
    await state.clear()

    # ------------------------------------------------------------------ #
    # если редактируем, достаём текущий профиль пользователя             #
    # ------------------------------------------------------------------ #
    user: UserRead | None = None
    if edit_mode:
        user = await get_user(message.chat.id)
        if user is None:
            # нельзя редактировать, если профиля нет
            await message.answer(SettingsMessages.profile_not_found)
            return
        # кладём все текущие поля в FSM‑storage, чтобы кнопка «⏭» знала что оставлять
        await state.update_data(edit_mode=True, **user.model_dump())
    else:
        # новая регистрация
        await state.update_data(edit_mode=False)

    current_name = user.full_name if edit_mode else None
    await message.answer(
        format_question(
            RegistrationMessages.ask_full_name,
            current_value=current_name,
            edit_mode=edit_mode,
        ),
        reply_markup=(
            RegistrationButtons.skip_button()
            if edit_mode
            else types.ReplyKeyboardRemove()
        ),
    )
    await state.set_state(RegistrationState.full_name)


# --------------------------------------------------------------------------- #
# steps                                                                       #
# --------------------------------------------------------------------------- #


async def get_full_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode: bool = data.get("edit_mode", False)

    if not is_skip(message):
        await state.update_data(full_name=message.text)

    await message.answer(
        format_question(
            RegistrationMessages.ask_age,
            current_value=data.get("age"),
            edit_mode=edit_mode,
        ),
        reply_markup=(
            RegistrationButtons.skip_button()
            if edit_mode
            else types.ReplyKeyboardRemove()
        ),
    )
    await state.set_state(RegistrationState.age)


async def get_age(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode: bool = data.get("edit_mode", False)

    if not is_skip(message):
        try:
            age = int(message.text)
            validate_age(age)
            await state.update_data(age=age)
        except ValueError:
            return await message.answer(RegistrationMessages.invalid_age)

    await message.answer(
        format_question(
            RegistrationMessages.ask_weight,
            current_value=data.get("weight"),
            edit_mode=edit_mode,
        ),
        reply_markup=(
            RegistrationButtons.skip_button()
            if edit_mode
            else types.ReplyKeyboardRemove()
        ),
    )
    await state.set_state(RegistrationState.weight)
    return None


async def get_weight(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        try:
            await state.update_data(weight=float(message.text))
        except ValueError:
            return await message.answer(RegistrationMessages.invalid_weight)

    await message.answer(
        format_question(
            RegistrationMessages.ask_height,
            current_value=data.get("height"),
            edit_mode=edit_mode,
        ),
        reply_markup=(
            RegistrationButtons.skip_button()
            if edit_mode
            else types.ReplyKeyboardRemove()
        ),
    )
    await state.set_state(RegistrationState.height)
    return None


async def get_height(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        try:
            await state.update_data(height=float(message.text))
        except ValueError:
            return await message.answer(RegistrationMessages.invalid_height)

    await message.answer(
        format_question(
            RegistrationMessages.ask_contraindications,
            current_value=data.get("contraindications"),
            edit_mode=edit_mode,
        ),
        reply_markup=RegistrationButtons.contraindications_list(),
    )
    await state.set_state(RegistrationState.contraindications)
    return None


async def get_contraindications(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        await state.update_data(contraindications=message.text)

    await message.answer(
        format_question(
            RegistrationMessages.ask_goal,
            current_value=data.get("goal"),
            edit_mode=edit_mode,
        ),
        reply_markup=RegistrationButtons.goals(),
    )
    await state.set_state(RegistrationState.goal)


async def get_goal(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        await state.update_data(goal=message.text)

    await message.answer(
        format_question(
            RegistrationMessages.ask_training_place,
            current_value=data.get("training_place"),
            edit_mode=edit_mode,
        ),
        reply_markup=RegistrationButtons.training_places(),
    )
    await state.set_state(RegistrationState.training_place)


async def get_place(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        await state.update_data(training_place=message.text)

    await message.answer(
        format_question(
            RegistrationMessages.ask_training_time,
            current_value=data.get("training_time"),
            edit_mode=edit_mode,
        ),
        reply_markup=(
            RegistrationButtons.skip_button()
            if edit_mode
            else types.ReplyKeyboardRemove()
        ),
    )
    await state.set_state(RegistrationState.training_time)


async def get_time(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    if not is_skip(message):
        parsed = parse_time(message.text)
        if not parsed:
            await message.answer(RegistrationMessages.invalid_time_format)
            return

        await state.update_data(training_time=parsed)

    await state.update_data(training_days=data.get("training_days", []))
    await message.answer(
        RegistrationMessages.ask_training_days,
        reply_markup=make_training_days_keyboard(list(data.get("training_days", []))),
    )
    await state.set_state(RegistrationState.training_days)
    return


async def toggle_day(
    callback: CallbackQuery, callback_data: ToggleDayCallback, state: FSMContext
) -> None:
    day = callback_data.day
    data = await state.get_data()
    selected = set(data.get("training_days", []))

    if day in selected:
        selected.remove(day)
    else:
        selected.add(day)

    await state.update_data(training_days=list(selected))
    await callback.message.edit_reply_markup(
        reply_markup=make_training_days_keyboard(list(selected))
    )
    await callback.answer()


async def confirm_days(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode: bool = data.get("edit_mode", False)

    if not data.get("training_days"):
        return await callback.answer(
            RegistrationMessages.empty_days_alert, show_alert=True
        )

    await callback.message.answer(
        format_question(
            RegistrationMessages.ask_notes,
            current_value=data.get("notes"),
            edit_mode=edit_mode,
        ),
        reply_markup=(
            RegistrationButtons.skip_button()
            if edit_mode
            else types.ReplyKeyboardRemove()
        ),
    )

    await state.set_state(RegistrationState.notes)
    await callback.answer()
    return None


# --------------------------------------------------------------------------- #
# finish                                                                      #
# --------------------------------------------------------------------------- #


async def finish_registration(
    message: Message, state: FSMContext, dialog_manager: DialogManager
) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        await state.update_data(notes=message.text)

    data = await state.get_data()

    try:
        user_data = UserCreate(**data, telegram_id=message.from_user.id)
    except ValidationError as e:
        logger.warning("Invalid registration data", error=str(e), raw=data)
        await message.answer(RegistrationMessages.registration_invalid_data)
        await state.clear()
        await dialog_manager.start(MainMenu.START, mode=StartMode.RESET_STACK)
        return

    try:
        logger.debug("Try to create or update user with data: %s", user_data)
        await create_or_update_user(user_data)
        if not edit_mode:  # генерируем коды только при первичной регистрации
            codes = await get_backup_codes(message.from_user.id)
            await message.answer(BackupCodeMessages.full(codes), parse_mode="HTML")
    except httpx.HTTPStatusError as e:
        logger.exception(
            "Backend returned error on user creation",
            status_code=e.response.status_code,
            response_text=e.response.text,
            url=str(e.request.url),
        )
        await message.answer(RegistrationMessages.registration_backend_error)
        return
    except httpx.RequestError as e:
        logger.exception("Connection error while contacting backend", details=str(e))
        await message.answer(RegistrationMessages.registration_backend_unavailable)
        return

    await message.answer(
        (
            RegistrationMessages.registration_success
            if not edit_mode
            else "✅Профиль обновлён!"
        ),
    )
    await state.clear()
    await dialog_manager.start(MainMenu.START, mode=StartMode.RESET_STACK)
