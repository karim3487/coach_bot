from aiogram.types import Message
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Cancel

from coach_bot.exceptions.api import BackupCodeInvalidOrUsed, TelegramIDAlreadyLinked, CoachApiClientError
from coach_bot.states.user import CodeLogin, UserMainMenu
from aiogram_dialog import DialogManager, StartMode
from coach_bot.services.coach_api import (
    api_client,
)


async def on_code_entered(
        message: Message, widget: TextInput, dialog_manager: DialogManager, code: str,
):
    telegram_id = message.from_user.id

    try:
        await api_client.auth_with_backup_code(code, telegram_id)
    except BackupCodeInvalidOrUsed:
        await message.answer("❌ Неверный или уже использованный код. Попробуйте снова.")
        return
    except TelegramIDAlreadyLinked:
        await message.answer("❌ Ваш Telegram-аккаунт уже привязан к другому профилю.")
        return
    except CoachApiClientError:
        await message.answer("❌ Не удалось проверить код. Пожалуйста, попробуйте позже.")
        return

    await dialog_manager.start(UserMainMenu.menu, mode=StartMode.RESET_STACK)


code_login_dialog = Dialog(
    Window(
        Const("🔐 Ведите ваш резервный код:"),
        TextInput(id="code", on_success=on_code_entered),
        Cancel(Const("⬅️ Назад")),
        state=CodeLogin.enter_code,
    ),
)
