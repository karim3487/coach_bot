from typing import Any


def is_valid_input(field: str, value: str) -> bool:
    try:
        if field == "age":
            return value.isdigit() and (0 < int(value) < 120)
        if field == "weight":
            return 20 <= float(value.replace(",", ".")) <= 300
        if field == "height":
            return 50 <= float(value.replace(",", ".")) <= 250
        if field == "name":
            return bool(value)
        if field == "preferred_time":
            import re

            return bool(re.match(r"^(2[0-3]|[01]?[0-9]):[0-5][0-9]$", value))
        return True
    except Exception:
        return False


def get_validation_error_message(field: str) -> str:
    return {
        "age": "❌ Укажите корректный возраст от 1 до 119 лет.",
        "weight": "❌ Вес должен быть числом от 20 до 300 кг.",
        "height": "❌ Рост должен быть числом от 50 до 250 см.",
        "name": "❌ Имя не может быть пустым.",
        "preferred_time": "❌ Время должно быть в формате ЧЧ:ММ, например: 18:30.",
    }.get(field, "❌ Некорректное значение.")


def parse_input(field: str, raw: str) -> Any:
    if field in {"weight", "height"}:
        return float(raw.replace(",", "."))
    if field == "age":
        return int(raw)
    return raw.strip()
