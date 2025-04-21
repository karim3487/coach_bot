from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    START = State()


class Settings(StatesGroup):
    START = State()


class Profile(StatesGroup):
    SHOW = State()
    EDIT = State()
