from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets import kbd

from coach_bot.dialogs.common.handlers.on_not_implemented import on_not_implemented
from coach_bot.dialogs.user_plan.getters import user_plan_getter
from coach_bot.states.user import UserPlanMenu, UserMainMenu, UserSchedule


async def on_show_schedule_clicked(callback: CallbackQuery, button: kbd.Button, manager: DialogManager):
    manager.dialog_data["page"] = 1
    await manager.start(UserSchedule.menu, mode=StartMode.RESET_STACK)


user_plan_dialog = Dialog(
    Window(
        Format("{plan_text}"),
        kbd.Row(
            kbd.Button(Const("📋 Расписание"), id="schedule", on_click=on_show_schedule_clicked),
            kbd.Button(Const("📈 Мой прогресс"), id="progress_plan", on_click=on_not_implemented),
        ),
        kbd.Row(
            kbd.Start(Const("⬅️ Назад в меню"), id="back", state=UserMainMenu.menu),
        ),
        state=UserPlanMenu.menu,
        getter=user_plan_getter,
    ),
)
