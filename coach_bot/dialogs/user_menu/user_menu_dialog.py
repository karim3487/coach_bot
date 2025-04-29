from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets import kbd
from coach_bot.dialogs.user_menu.getters import main_menu_getter
from coach_bot.dialogs.user_menu.handlers.main_menu_handlers import (
    on_start_workout_clicked,
    on_progress_clicked,
    on_my_plan_clicked,
)
from coach_bot.states.user import UserMainMenu, Settings

main_menu_dialog = Dialog(
    Window(
        Format("🏠 Добро пожаловать, {user_name}! Что вы хотите сделать?"),
        kbd.Row(
            kbd.Button(Const("🏋️ Начать тренировку"), id="start_workout", on_click=on_start_workout_clicked),
            kbd.Button(Const("📈 Прогресс"), id="progress", on_click=on_progress_clicked),
        ),
        kbd.Row(
            kbd.Button(Const("📋 Мой план"), id="my_plan", on_click=on_my_plan_clicked),
            kbd.Button(Const("🎯 Моя цель"), id="my_goal", on_click=lambda *args, **kwargs: None),
        ),
        kbd.Row(
            kbd.Start(Const("⚙️ Настройки"), id="settings", state=Settings.menu),
        ),
        state=UserMainMenu.menu,
        getter=main_menu_getter,
    ),
)
