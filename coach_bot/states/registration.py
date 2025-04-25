from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    full_name = State()
    gender = State()
    age = State()
    weight = State()
    height = State()
    contraindications = State()
    goal = State()
    training_location = State()
    training_time = State()
    training_days = State()
    notes = State()
