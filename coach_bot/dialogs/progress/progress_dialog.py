from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets import text, kbd

from coach_bot.dialogs.progress.getter import progress_getter
from coach_bot.states.user import UserProgress, UserMainMenu


def pagination_buttons():
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


progress_dialog = Dialog(
    Window(
        text.Format("{progress_text}"),
        pagination_buttons(),
        kbd.Row(
            kbd.Start(text.Const("⬅️ Назад в меню"), id="back", state=UserMainMenu.menu),
        ),
        state=UserProgress.menu,
        getter=progress_getter,
    ),
)
