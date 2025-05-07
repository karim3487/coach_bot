from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets import kbd
from aiogram_dialog.widgets.text import Const, Format

from coach_bot.dialogs.common.widgets.buttons import back_button
from coach_bot.dialogs.plan_create.getters import programs_getter
from coach_bot.dialogs.plan_create import handlers
from coach_bot.states.user import PlanCreateMenu, UserMainMenu


def pagination_buttons():
    return kbd.Row(
        kbd.Button(Const("⏮"), id="first", on_click=switch_page(1)),
        kbd.Button(Const("◀️"), id="prev", on_click=switch_relative_page(-1)),
        kbd.Button(Const("▶️"), id="next", on_click=switch_relative_page(1)),
        kbd.Button(Const("⏭"), id="last", on_click=switch_last_page),
    )


async def switch_last_page(c: CallbackQuery, b: kbd.Button, m: DialogManager):
    total = m.dialog_data.get("total_pages", 1)
    m.dialog_data["page"] = total
    await m.show()


def switch_page(page: int):
    async def handler(c: CallbackQuery, b: kbd.Button, m: DialogManager):
        m.dialog_data["page"] = page
        await m.show()

    return handler


def switch_relative_page(offset: int):
    async def handler(c: CallbackQuery, b: kbd.Button, m: DialogManager):
        current = m.dialog_data.get("page", 1)
        total = m.dialog_data.get("total_pages", 1)
        new_page = max(1, min(total, current + offset))
        m.dialog_data["page"] = new_page
        print("New PAGE!!!", new_page)
        await m.show()

    return handler


program_selection_window = Window(
    Format("📚 Выберите программу:\n\n"
           "{programs_description}\n\n"
           "📄 Страница {current_page} из {total_pages}"),
    kbd.Select(
        Format("{item[item_number]}"),
        id="program_select",
        items="program_buttons",
        item_id_getter=lambda x: str(x["id"]),
        on_click=handlers.on_program_selected,
    ),
    pagination_buttons(),
    back_button,
    state=PlanCreateMenu.choose_program,
    getter=programs_getter,
)

plan_create_dialog = Dialog(
    Window(
        Const("📋 У вас ещё нет плана тренировок. Что вы хотите сделать?"),
        kbd.Button(Const("📚 Выбрать программу"), id="choose_program", on_click=handlers.on_choose_program),
        kbd.Button(Const("🤖 Создать автоматически"), id="auto_generate", on_click=handlers.on_auto_generate),
        kbd.Start(Const("⬅️ Назад в меню"), id="back", state=UserMainMenu.menu),
        state=PlanCreateMenu.start,
    ),
    program_selection_window,
)
