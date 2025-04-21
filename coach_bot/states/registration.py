from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    full_name = State()
    age = State()
    weight = State()
    height = State()
    contraindications = State()
    goal = State()
    training_place = State()
    training_time = State()
    training_days = State()
    notes = State()
