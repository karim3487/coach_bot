import aiogram

from coach_bot.keyboards.default.consts import DefaultConstructor
from coach_bot.models.schemas import (
    ContraindicationsEnum,
    GenderEnum,
    TrainingLocationEnum,
)
from coach_bot.services.user_client import get_goals
from coach_bot.utils.utils import enum_to_list


class RegistrationButtons(DefaultConstructor):
    @staticmethod
    def genders() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1, 1]
        btns = enum_to_list(GenderEnum)
        return RegistrationButtons._create_kb(btns, schema)

    @staticmethod
    async def goals() -> aiogram.types.ReplyKeyboardMarkup:
        # btns = [
        #     "Набор массы",
        #     "Снижение жира",
        #     "Рельеф",
        #     "Сила",
        #     "Выносливость",
        #     "Общее здоровье",
        # ]
        btns = await get_goals()
        schema = [2] * (len(btns) // 2) + ([len(btns) % 2] if len(btns) % 2 else [])
        return RegistrationButtons._create_kb(btns, schema)

    @staticmethod
    def contraindications_list() -> aiogram.types.ReplyKeyboardMarkup:
        btns = [c.value.title() for c in ContraindicationsEnum]
        schema = [2] * (len(btns) // 2) + ([len(btns) % 2] if len(btns) % 2 else [])
        return RegistrationButtons._create_kb(btns, schema)

    @staticmethod
    def training_locations() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1, 1, 1]
        btns = enum_to_list(TrainingLocationEnum)
        return RegistrationButtons._create_kb(btns, schema)

    @staticmethod
    def skip_button() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["⏭️Оставить текущее"]
        return RegistrationButtons._create_kb(btns, schema, one_time_keyboard=True)
