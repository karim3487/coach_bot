from coach_bot.dialogs.code_login import code_login_dialog
from coach_bot.dialogs.guest_menu import guest_menu_dialog
from coach_bot.dialogs.profile_form.profile_form import profile_form_dialog
from coach_bot.dialogs.user_menu.profile_dialog import profile_dialog
from coach_bot.dialogs.user_menu.user_menu import main_menu, settings_dialog

dialogs = [
    code_login_dialog,
    guest_menu_dialog,
    profile_form_dialog,
    main_menu,
    settings_dialog,
    profile_dialog,
]
