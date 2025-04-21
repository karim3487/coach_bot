import asyncio
import os
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, setup_dialogs, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format

from coach_bot.services.user_client import get_user


# ───────────────────────── states ───────────────────────── #
class MainMenu(StatesGroup):
    START = State()


class Settings(StatesGroup):
    START = State()


class Profile(StatesGroup):
    SHOW = State()  # экран просмотра анкеты
    EDIT = State()  # запускает твою FSM‑анкету


# ───────────────────────── getters ──────────────────────── #
async def main_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    user = await get_user(dialog_manager.event.from_user.id)
    is_authorized = bool(user)  # Проверяем, авторизован ли пользователь
    usr = dialog_manager.event.from_user
    return {
        "name": usr.first_name or usr.username,
        "is_authorized": is_authorized,
    }


async def profile_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    user = await get_user(dialog_manager.event.from_user.id)
    if user:
        user_dict = user.model_dump()
        user_dict["training_time"] = user.training_time.strftime("%H:%M")
        user_dict["training_days"] = ", ".join(user.training_days)
        return user_dict


# ───────────────────────── windows ──────────────────────── #
main_menu = Dialog(
    Window(
        Format("👋 Привет, {name}! Выберите действие:"),
        Row(
            Button(
                Const("🏋️ Начать тренировку"), id="workout", on_click=lambda c, d, m: ...
            ),
            Button(Const("📊 Прогресс"), id="progress", on_click=lambda c, d, m: ...),
        ),
        Row(
            Button(Const("⚙️ Настройки"), id="settings", on_click=lambda c, d, m: ...),
        ),
        Row(
            Button(Const("👤 Авторизоваться"), id="login", when="not is_authorized"),
            Button(Const("🚪 Выйти"), id="logout", when="is_authorized"),
        ),
        getter=main_getter,
        state=MainMenu.START,
    ),
)

settings_dialog = Dialog(
    Window(
        Const("⚙️ Настройки"),
        Row(
            Button(Const("👤 Профиль"), id="profile", on_click=lambda c, d, m: ...),
            Button(
                Const("🔐 Сменить код входа"),
                id="chg_code",
                on_click=lambda c, d, m: ...,
            ),
        ),
        Row(Cancel(Const("◀️ Назад"))),
        state=Settings.START,
    ),
)

profile_dialog = Dialog(
    Window(
        Format(
            "<b>👤 Профиль</b>\n"
            "ФИО: {full_name}\n"
            "Возраст: {age}\n"
            "Вес: {weight} кг\n"
            "Рост: {height} см\n"
            "Цель: {goal}\n"
            "Место тренировок: {training_place}\n"
            "Время: {training_time}\n"
            "Дни: {training_days}\n",
        ),
        Row(
            Button(
                Const("✏️ Изменить"), id="edit_profile", on_click=lambda c, d, m: ...
            ),
            Cancel(Const("◀️ Назад")),
        ),
        state=Profile.SHOW,
        getter=profile_getter,
    ),
)

# ───────────────────────── bot setup ────────────────────── #
router = Router()


@router.message(CommandStart())
async def cmd_start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenu.START)


async def main():
    bot = Bot(
        token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()
    dp.include_router(main_menu)
    dp.include_router(settings_dialog)
    dp.include_router(profile_dialog)
    dp.include_router(router)
    setup_dialogs(dp)

    await dp.start_polling(bot, parse_mode=ParseMode.HTML)


asyncio.run(main())
