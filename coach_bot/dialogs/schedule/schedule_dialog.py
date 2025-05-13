from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets import kbd
from aiogram_dialog.widgets import text

from coach_bot.dialogs.schedule.getters import schedule_getter
from coach_bot.dialogs.user_menu.handlers.main_menu_handlers import on_my_plan_clicked
from coach_bot.states.user import UserSchedule

ID_SCROLL_SCHEDULE = "scroll_schedule"


def schedule_pagination_buttons():
    return kbd.Row(
        kbd.Button(text.Const("⏮"), id="first", on_click=switch_page(1)),
        kbd.Button(text.Const("◀️"), id="prev", on_click=switch_relative_page(-1)),
        kbd.Button(text.Const("▶️"), id="next", on_click=switch_relative_page(1)),
        kbd.Button(text.Const("⏭"), id="last", on_click=switch_last_page),
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
        await m.show()

    return handler


schedule_dialog = Dialog(
    Window(
        text.Format("📅 <b>Ваше расписание:</b>\n\n{schedule_text}\n\n"
                    "📄 Страница {current_page} из {total_pages}"),
        schedule_pagination_buttons(),
        kbd.Button(text.Const("⬅️ Назад"), id="my_plan", on_click=on_my_plan_clicked),
        getter=schedule_getter,
        state=UserSchedule.menu,
    ),
)
