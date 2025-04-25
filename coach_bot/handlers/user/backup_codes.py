import asyncio

from aiogram import types
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from coach_bot.constants.messages import BackupCodeMessages
from coach_bot.services.user_client import get_backup_codes


async def backup_codes_cmd(
    message: types.Message,
) -> None:
    """
    /backup_codes  – generate N fresh backup codes and show them once.
    """
    user_id = message.from_user.id

    # 1) generate raw codes
    codes = await get_backup_codes(user_id)  # returns List[str]

    sent = await message.answer(
        BackupCodeMessages.full(codes),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    # 3) auto‑delete after 60 s
    await asyncio.sleep(60)
    await sent.delete()


async def on_get_backup_codes(
    c: types.CallbackQuery,
    _btn: Button,
    manager: DialogManager,
) -> None:
    await c.answer()
    await manager.done()

    user_id = c.from_user.id

    codes = await get_backup_codes(user_id)

    sent = await c.message.answer(
        BackupCodeMessages.full(codes),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    await asyncio.sleep(10)
    await sent.delete()
