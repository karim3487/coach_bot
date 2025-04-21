from aiogram import types

from coach_bot.keyboards.default.consts import DefaultConstructor


class MainMenuButtons(DefaultConstructor):
    @staticmethod
    def main_menu() -> types.ReplyKeyboardMarkup:
        schema = [1, 1]
        btns = [
            "📝 Пройти регистрацию",
            "🔑 Войти по коду",
        ]
        return MainMenuButtons._create_kb(btns, schema)
