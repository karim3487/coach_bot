from aiogram.fsm.state import StatesGroup, State


class UserMainMenu(StatesGroup):
    menu = State()


class Settings(StatesGroup):
    menu = State()


class Profile(StatesGroup):
    show = State()
    edit_name = State()
    edit_email = State()
    edit_phone = State()
    edit_password = State()


class Guest(StatesGroup):
    menu = State()


class CodeLogin(StatesGroup):
    enter_code = State()


class Registration(StatesGroup):
    fill_name = State()


class ProfileForm(StatesGroup):
    name = State()
    age = State()
    weight = State()
    height = State()
    gender = State()
    training_location = State()
    contraindications = State()
    available_days = State()
    preferred_time = State()
    goal = State()
    confirm = State()


class PlanCreateMenu(StatesGroup):
    start = State()
    choose_program = State()


class UserPlanMenu(StatesGroup):
    menu = State()


class UserWorkout(StatesGroup):
    enter_note = State()
    enter_weight = State()
    enter_duration = State()
    enter_reps = State()
    overview = State()
    exercise = State()
    completed = State()
    no_workout = State()
    enter_progress = State()


class UserSchedule(StatesGroup):
    menu = State()


class UserProgress(StatesGroup):
    menu = State()
