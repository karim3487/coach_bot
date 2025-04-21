from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from coach_bot.keyboards.inline.callbacks import ConfirmDaysCallback, ToggleDayCallback

DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def make_training_days_keyboard(selected: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for day in DAYS:
        builder.button(
            text=f"✅ {day}" if day in selected else day,
            callback_data=ToggleDayCallback(day=day),
        )

    builder.button(
        text="Готово",
        callback_data=ConfirmDaysCallback(),
    )

    builder.adjust(3, 2, 2, 1)
    return builder.as_markup()
