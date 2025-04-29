import logging
from aiogram import types
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets import kbd
from coach_bot.services.coach_api import api_client

logger = logging.getLogger(__name__)


async def on_get_backup_codes_clicked(callback: types.CallbackQuery, button: kbd.Button, manager: DialogManager):
    try:
        await manager.mark_closed()

        telegram_id = callback.from_user.id
        backup_codes = await api_client.get_backup_codes(telegram_id)
        codes_text = "\n".join(backup_codes)

        file_bytes = codes_text.encode("utf-8")
        document = types.BufferedInputFile(file_bytes, filename="backup_codes.txt")

        await callback.message.answer_document(
            document=document,
            caption=f"🔐 Ваши новые резервные коды:\n\n<pre>{codes_text}</pre>\n‼️ Сохраните их в безопасном месте.",
        )

        await callback.answer()
    except Exception as e:
        logger.exception("Failed to generate backup codes", exc_info=e)
        await callback.answer("❌ Ошибка при получении кодов.", show_alert=True)
