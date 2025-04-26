from functools import partial
from typing import Any
from aiogram import types
from aiogram_dialog import ChatEvent, DialogManager
from aiogram_dialog.widgets.input import MessageInput

from coach_bot.dialogs.profile_form.handlers.validators import get_validation_error_message, is_valid_input, parse_input


async def on_text_input(
    message: types.Message, _: MessageInput, manager: DialogManager, field: str,
):
    value = message.text.strip()

    if not is_valid_input(field, value):
        await message.answer(get_validation_error_message(field))
        return

    manager.dialog_data[field] = parse_input(field, value)
    await manager.next()


async def on_selection(
    callback: ChatEvent, select: Any, manager: DialogManager, item_id: str, field: str,
):
    manager.dialog_data[field] = item_id
    await manager.next()


def selection_handler(field: str):
    return partial(on_selection, field=field)
