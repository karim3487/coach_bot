from aiogram import types
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets import kbd


async def on_not_implemented(
        callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager,
):
    await callback.answer("🚧 Пока не реализовано.")
