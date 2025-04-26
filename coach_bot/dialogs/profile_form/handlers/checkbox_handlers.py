from aiogram import types
from aiogram_dialog import ChatEvent, DialogManager
from aiogram_dialog.widgets.kbd import Button, ManagedCheckbox

from coach_bot.dialogs.profile_form.handlers.utils import update_selection


async def on_day_changed(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager,
):
    update_selection(manager, checkbox, "available_days")


async def on_contraindication_changed(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager,
):
    update_selection(manager, checkbox, "contraindications")


async def on_days_next(_: types.CallbackQuery, __: Button, manager: DialogManager):
    selected_days = manager.dialog_data.get("available_days")

    if not selected_days:
        query: types.CallbackQuery = manager.event
        await query.answer(
            text="❌ Пожалуйста, выберите хотя бы один день.",
            show_alert=True,
        )
        return

    await manager.next()


async def on_contraindication_next(
    _: types.CallbackQuery, __: Button, manager: DialogManager,
):
    selected_contraindications = manager.dialog_data.get("contraindications")

    if not selected_contraindications:
        query: types.CallbackQuery = manager.event
        await query.answer(
            text="❌ Пожалуйста, выберите хотя бы одно противопоказание.",
            show_alert=True,
        )
        return

    await manager.next()
