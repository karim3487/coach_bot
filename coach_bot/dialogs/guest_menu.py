from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets import kbd
from aiogram_dialog.widgets.text import Const
from coach_bot.states.user import Guest, CodeLogin, ProfileForm


guest_menu_dialog = Dialog(
    Window(
        Const("👋 Добро пожаловать! Вы еще не зарегистрированы"),
        kbd.Column(
            kbd.Start(Const("🔐 Войти с помощью кода"), id="login_code", state=CodeLogin.enter_code),
            kbd.Start(Const("📝 Зарегистрироваться"), id="register", state=ProfileForm.name),
        ),
        state=Guest.menu,
    ),
)
