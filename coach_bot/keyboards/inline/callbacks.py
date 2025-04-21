from aiogram.filters.callback_data import CallbackData


class Action(CallbackData, prefix="act"):
    action: str


class ToggleDayCallback(CallbackData, prefix="day"):
    day: str


class ConfirmDaysCallback(CallbackData, prefix="days_done"):
    pass
