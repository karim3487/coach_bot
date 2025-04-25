from enum import Enum
from typing import Any

import httpx
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from pydantic import ValidationError
from slugify import slugify
from structlog import get_logger

from coach_bot.constants.messages import (
    BackupCodeMessages,
    RegistrationMessages,
    SettingsMessages,
)
from coach_bot.keyboards.default.registration import RegistrationButtons
from coach_bot.keyboards.inline.callbacks import ToggleDayCallback
from coach_bot.keyboards.inline.user.weekly import make_training_days_keyboard
from coach_bot.models.schemas import (
    ClientProfileCreate,
    ClientProfileShort,
    ContraindicationsEnum,
    GenderEnum,
)
from coach_bot.services.user_client import (
    create_or_update_user,
    get_backup_codes,
    get_goal_by_slug,
    get_user,
)
from coach_bot.states.menu import MainMenu
from coach_bot.states.registration import RegistrationState
from coach_bot.utils.parse_time import parse_time
from coach_bot.utils.utils import enum_to_list

logger = get_logger(__name__)


# ---------------------------- Helper Functions ---------------------------- #

async def process_profile(
    data: dict, telegram_id: int, send_func, edit_mode: bool,
) -> bool:
    """
    Обрабатывает поле goal, создает/обновляет профиль и отправляет backup-коды.
    send_func: асинхронная функция для отправки сообщений (например, message.answer или bot.send_message)
    Возвращает True при успешном выполнении, иначе False.
    """
    # Обработка поля цели (goal)
    goal_slug = data.get("goal")
    if goal_slug:
        goal_obj = await get_goal_by_slug(goal_slug)
        if not goal_obj:
            await send_func(RegistrationMessages.goal_not_found)
            return False
        data["goal"] = goal_obj.id

    try:
        user_profile = ClientProfileCreate(**data, telegram_id=telegram_id)
        logger.debug("Creating/updating profile", user=user_profile.model_dump())
        await create_or_update_user(user_profile)
        if not edit_mode:  # генерируем backup-коды только при первичной регистрации
            codes = await get_backup_codes(telegram_id)
            await send_func(BackupCodeMessages.full(codes), parse_mode="HTML")
    except ValidationError as e:
        logger.warning("Invalid registration data", error=str(e), raw=data)
        await send_func(RegistrationMessages.registration_invalid_data)
        return False
    except httpx.HTTPStatusError as e:
        logger.exception("Backend returned HTTP error", response=e.response)
        await send_func(RegistrationMessages.registration_backend_error)
        return False
    except httpx.RequestError as e:
        logger.exception("Network error contacting backend", details=str(e))
        await send_func(RegistrationMessages.registration_backend_unavailable)
        return False

    return True


def format_question(label: str, current_value: Any | None, *, edit_mode: bool) -> str:
    """
    Форматирование вопроса с подсказкой текущего значения если включен режим редактирования.
    """
    if edit_mode and current_value is not None:
        if isinstance(current_value, Enum):
            current_value = current_value.value.title()
        return (
            f"{label}\n\n"
            f"<b>Текущее значение:</b> {current_value}\n"
            f"Введите новое или нажмите «⏭️Оставить текущее»"
        )
    return label


def is_skip(msg: Message) -> bool:
    return msg.text == "⏭️Оставить текущее"


# ---------------------------- Handlers: Начало и редактирование ---------------------------- #

async def on_edit_profile(
    c: types.CallbackQuery,
    _btn: Button,
    manager: DialogManager,
) -> None:
    # Закрываем текущий диалог и запускаем анкету в режиме редактирования.
    await manager.reset_stack()
    state = manager.middleware_data["state"]
    await start_registration(c.message, state, edit_mode=True)


async def on_edit(
    c: types.CallbackQuery,
    _b: Button,
    manager: DialogManager,
) -> None:
    await manager.done()  # Закрываем диалог меню
    await start_registration(c.message, manager.middleware_data["state"], edit_mode=True)


async def start_registration(
    message: Message,
    state: FSMContext,
    *,  # только именованные аргументы
    edit_mode: bool = False,
) -> None:
    """
    Запуск регистрации или редактирования профиля.
    """
    await state.clear()

    user: ClientProfileShort | None = None
    if edit_mode:
        user = await get_user(message.chat.id)
        if user is None:
            await message.answer(SettingsMessages.profile_not_found)
            return
        # Загружаем текущие данные профиля в FSM‑storage
        await state.update_data(edit_mode=True, **user.model_dump())
    else:
        await state.update_data(edit_mode=False)

    current_name = user.name if edit_mode else None
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


# ---------------------------- Handlers: Шаги регистрации ---------------------------- #

async def get_full_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode: bool = data.get("edit_mode", False)
    if not is_skip(message):
        await state.update_data(name=message.text)

    await message.answer(
        format_question(
            RegistrationMessages.ask_gender,
            current_value=data.get("gender"),
            edit_mode=edit_mode,
        ),
        reply_markup=(
            RegistrationButtons.skip_button()
            if edit_mode
            else RegistrationButtons.genders()
        ),
    )
    await state.set_state(RegistrationState.gender)


async def get_gender(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        if message.text not in enum_to_list(GenderEnum):
            return await message.answer(
                "Пожалуйста, выберите пол из предложенных вариантов.",
            )
        await state.update_data(gender=message.text.lower())

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
            # Функция валидации выбрасывает исключение при неверном возрасте
            if not (10 <= age <= 100):
                raise ValueError
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


async def get_contraindications(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)

    if not is_skip(message):
        if message.text not in enum_to_list(ContraindicationsEnum):
            return await message.answer(
                "Пожалуйста, выберите противопоказания из предложенных вариантов.",
            )
        await state.update_data(contraindications=message.text.lower())

    markup = await RegistrationButtons.goals()
    await message.answer(
        format_question(
            RegistrationMessages.ask_goal,
            current_value=data.get("goal"),
            edit_mode=edit_mode,
        ),
        reply_markup=markup,
    )
    await state.set_state(RegistrationState.goal)


async def get_goal(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)
    if not is_skip(message):
        # Преобразуем ввод в slug
        await state.update_data(goal=slugify(message.text))

    await message.answer(
        format_question(
            RegistrationMessages.ask_training_location,
            current_value=data.get("training_location"),
            edit_mode=edit_mode,
        ),
        reply_markup=RegistrationButtons.training_locations(),
    )
    await state.set_state(RegistrationState.training_location)


async def get_place(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)
    if not is_skip(message):
        await state.update_data(training_location=message.text.lower())

    await message.answer(
        format_question(
            RegistrationMessages.ask_training_time,
            current_value=data.get("preferred_time"),
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
        await state.update_data(preferred_time=parsed)

    await state.update_data(available_days=data.get("training_days", []))
    await message.answer(
        RegistrationMessages.ask_training_days,
        reply_markup=make_training_days_keyboard(list(data.get("training_days", []))),
    )
    await state.set_state(RegistrationState.training_days)


async def toggle_day(
    callback: CallbackQuery, callback_data: ToggleDayCallback, state: FSMContext,
) -> None:
    data = await state.get_data()
    selected = set(data.get("available_days", []))
    day = callback_data.day

    if day in selected:
        selected.remove(day)
    else:
        selected.add(day)

    await state.update_data(available_days=list(selected))
    await callback.message.edit_reply_markup(
        reply_markup=make_training_days_keyboard(list(selected)),
    )
    await callback.answer()


# ---------------------------- Handlers: Завершение регистрации ---------------------------- #

async def confirm_days(
    callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager,
) -> None:
    await callback.answer()
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)
    telegram_id = callback.from_user.id
    bot = callback.bot

    # Определяем send_func для работы с ботом
    async def send_func(text: str, **kwargs) -> None:
        await bot.send_message(telegram_id, text, **kwargs)

    # Обработка профиля (проверка, создание/обновление)
    if not await process_profile(data, telegram_id, send_func, edit_mode):
        await state.clear()
        return

    # Отправляем сообщение об успешном завершении регистрации/редактирования
    await bot.send_message(
        telegram_id,
        RegistrationMessages.registration_success if not edit_mode else "✅Профиль обновлён!",
    )
    await state.clear()
    await dialog_manager.start(MainMenu.START, mode=StartMode.RESET_STACK)


async def finish_registration(
    message: Message, state: FSMContext, dialog_manager: DialogManager,
) -> None:
    data = await state.get_data()
    edit_mode = data.get("edit_mode", False)
    if not is_skip(message):
        await state.update_data(notes=message.text)

    data = await state.get_data()
    telegram_id = message.from_user.id

    # Определяем send_func для работы с сообщениями из объекта Message
    async def send_func(text: str, **kwargs) -> None:
        await message.answer(text, **kwargs)

    if not await process_profile(data, telegram_id, send_func, edit_mode):
        await state.clear()
        return

    await send_func(
        RegistrationMessages.registration_success
        if not edit_mode
        else "✅Профиль обновлён!",
    )
    await state.clear()
    await dialog_manager.start(MainMenu.START, mode=StartMode.RESET_STACK)
