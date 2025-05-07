from coach_bot.dialogs.code_login import code_login_dialog
from coach_bot.dialogs.guest_menu import guest_menu_dialog
from coach_bot.dialogs.plan_create.plan_create_dialog import plan_create_dialog
from coach_bot.dialogs.profile_form.profile_form_dialog import profile_form_dialog
from coach_bot.dialogs.schedule.schedule_dialog import schedule_dialog
from coach_bot.dialogs.user_menu.profile_dialog import profile_dialog
from coach_bot.dialogs.user_menu.user_menu_dialog import main_menu_dialog
from coach_bot.dialogs.user_menu.settings_menu_dialog import settings_dialog
from coach_bot.dialogs.user_plan.user_plan_dialog import user_plan_dialog
from coach_bot.dialogs.workout.workout_dialog import workout_dialog

dialogs = [
    code_login_dialog,
    guest_menu_dialog,
    profile_form_dialog,
    main_menu_dialog,
    settings_dialog,
    profile_dialog,
    plan_create_dialog,
    user_plan_dialog,
    workout_dialog,
    schedule_dialog,
]
