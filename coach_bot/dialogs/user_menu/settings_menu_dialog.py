from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets import kbd
from coach_bot.dialogs.user_menu.handlers.settings_handlers import on_get_backup_codes_clicked
from coach_bot.states.user import Settings, UserMainMenu, Profile

settings_dialog = Dialog(
    Window(
        Const("⚙️ Настройки"),
        kbd.Row(
            kbd.Start(Const("👤 Профиль"), id="profile", state=Profile.show),
            kbd.Button(Const("🔐 Новые коды входа"), id="backup_codes", on_click=on_get_backup_codes_clicked),
        ),
        kbd.Row(
            kbd.Start(Const("⬅️ Назад в меню"), id="back_to_main", state=UserMainMenu.menu),
        ),
        state=Settings.menu,
    ),
)
