from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter

from coach_bot import states
from coach_bot.filters import ChatTypeFilter, TextFilter
from coach_bot.handlers.user import backup_codes, login, registration, start
from coach_bot.keyboards.inline.callbacks import ConfirmDaysCallback, ToggleDayCallback


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())

    # Commands
    user_router.message.register(backup_codes.backup_codes_cmd, Command("backup_codes"))

    # FSM: Login user
    user_router.message.register(
        login.ask_login_code,
        TextFilter("🔑 Войти по коду"),  # текст кнопки / команды
    )
    user_router.message.register(
        login.submit_login_code,
        StateFilter(states.login.LoginState.code),
    )

    # FSM: Register User
    user_router.message.register(
        registration.start_registration,
        TextFilter("📝 Пройти регистрацию"),
    )
    user_router.message.register(
        registration.get_full_name,
        StateFilter(states.registration.RegistrationState.full_name),
    )
    user_router.message.register(
        registration.get_age,
        StateFilter(states.registration.RegistrationState.age),
    )
    user_router.message.register(
        registration.get_weight,
        StateFilter(states.registration.RegistrationState.weight),
    )
    user_router.message.register(
        registration.get_height,
        StateFilter(states.registration.RegistrationState.height),
    )
    user_router.message.register(
        registration.get_contraindications,
        StateFilter(states.registration.RegistrationState.contraindications),
    )
    user_router.message.register(
        registration.get_goal,
        StateFilter(states.registration.RegistrationState.goal),
    )
    user_router.message.register(
        registration.get_place,
        StateFilter(states.registration.RegistrationState.training_place),
    )
    user_router.message.register(
        registration.get_time,
        StateFilter(states.registration.RegistrationState.training_time),
    )

    # CALLBACKS — выбор дней
    user_router.callback_query.register(
        registration.toggle_day,
        ToggleDayCallback.filter(),
        StateFilter(states.registration.RegistrationState.training_days),
    )
    user_router.callback_query.register(
        registration.confirm_days,
        ConfirmDaysCallback.filter(),
        StateFilter(states.registration.RegistrationState.training_days),
    )

    user_router.message.register(
        registration.finish_registration,
        StateFilter(states.registration.RegistrationState.notes),
    )

    return user_router
