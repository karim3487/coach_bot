from aiogram.fsm.state import State, StatesGroup


class LoginState(StatesGroup):
    code = State()
