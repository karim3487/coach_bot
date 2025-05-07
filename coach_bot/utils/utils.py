from datetime import datetime, date, time
from enum import Enum
from typing import Any
from aiogram import types

from coach_bot.utils.constants import MONTHS_RU


def enum_to_list(enum: Enum) -> list[str]:
    return [item.value for item in enum]


def format_question(label: str, value: Any | None, *, edit_mode: bool) -> str:
    if edit_mode and value is not None:
        if isinstance(value, Enum):
            value = value.value.title()
        return f"{label}\n\n<b>Текущее значение:</b> {value}\nВведите новое или нажмите «⏭️Оставить текущее»"
    return label


def is_skip(msg: types.Message) -> bool:
    return msg.text == "⏭️Оставить текущее"


async def ask_step(
        message: types.Message,
        label: str,
        value: Any,
        edit_mode: bool,
        markup: types.ReplyKeyboardMarkup | None = None,
):
    await message.answer(
        format_question(label, value, edit_mode=edit_mode),
        reply_markup=markup if edit_mode else types.ReplyKeyboardRemove(),
    )


def format_datetime(date_obj: date, time_obj: time) -> str:
    dt = datetime.combine(date_obj, time_obj)
    return f"{dt.day} {MONTHS_RU[dt.month]} {dt.strftime('%H:%M')}"
