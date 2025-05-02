from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets import kbd
from aiogram_dialog.widgets.text import Const, Format

from coach_bot.dialogs.common.widgets.buttons import back_button
from coach_bot.dialogs.plan_create.getters import program_list_getter
from coach_bot.dialogs.plan_create import handlers
from coach_bot.states.user import PlanCreateMenu

ID_SCROLL_PROGRAMS = "scroll_programs"

program_selection_window = Window(
    Format("📚 Выберите программу из списка ниже:\n\n{programs_description}"),
    kbd.ScrollingGroup(
        kbd.Select(
            Format("{item[item_number]}"),
            id="program_select",
            items="program_buttons",
            item_id_getter=lambda x: str(x["id"]),
            on_click=handlers.on_program_selected,
        ),
        id=ID_SCROLL_PROGRAMS,
        width=3,
        height=5,
    ),
    back_button,
    state=PlanCreateMenu.choose_program,
    getter=program_list_getter,
)

plan_create_dialog = Dialog(
    Window(
        Const("📋 У вас ещё нет плана тренировок. Что вы хотите сделать?"),
        kbd.Button(Const("📚 Выбрать программу"), id="choose_program", on_click=lambda c, b, m: m.next()),
        kbd.Button(Const("🤖 Создать автоматически"), id="auto_generate", on_click=handlers.on_auto_generate),
        back_button,
        state=PlanCreateMenu.start,
    ),
    program_selection_window,
)
