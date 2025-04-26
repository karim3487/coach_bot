from aiogram_dialog.widgets.kbd import Button, Back, SwitchTo
from aiogram_dialog.widgets.text import Const

back_button = Back(Const("🔙 Назад"))
edit_button = SwitchTo(Const("🔁 Изменить"), id="restart", state=None)  # state задаётся динамически
confirm_button = Button(Const("✅ Подтвердить"), id="confirm", on_click=None)  # on_click задаёшь при создании
