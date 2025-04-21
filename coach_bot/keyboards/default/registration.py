import aiogram

from coach_bot.keyboards.default.consts import DefaultConstructor


class RegistrationButtons(DefaultConstructor):
    @staticmethod
    def goals() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [2, 2, 2]
        btns = [
            "Набор массы",
            "Снижение жира",
            "Рельеф",
            "Сила",
            "Выносливость",
            "Общее здоровье",
        ]
        return RegistrationButtons._create_kb(btns, schema)

    @staticmethod
    def contraindications_list() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [2, 2, 1]
        btns = [
            "Гипертония",
            "Проблемы с суставами",
            "Болезни сердца",
            "Проблемы с дыханием",
            "Нет",
        ]
        return RegistrationButtons._create_kb(btns, schema)

    @staticmethod
    def training_places() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1, 1, 1]
        btns = ["Дом", "Зал с инвентарём", "Уличная площадка"]
        return RegistrationButtons._create_kb(btns, schema)

    @staticmethod
    def skip_button() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["⏭️Оставить текущее"]
        return RegistrationButtons._create_kb(btns, schema, one_time_keyboard=True)
