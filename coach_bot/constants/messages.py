class RegistrationMessages:
    ask_full_name = "Введите ваше ФИО:"
    ask_age = "Ваш возраст?"
    invalid_age = "Введите возраст от 10 до 100."
    ask_weight = "Ваш вес (в кг)?"
    invalid_weight = "Введите корректный вес."
    ask_height = "Ваш рост (в см)?"
    invalid_height = "Введите корректный рост."
    ask_contraindications = "Есть ли противопоказания?"
    ask_goal = "Ваша цель?"
    ask_training_place = "Где будете тренироваться?"
    ask_training_time = "Во сколько обычно тренируетесь? (например 20:00)"
    invalid_time_format = "Введите корректное время в формате ЧЧ:ММ"
    ask_training_days = "Выберите дни, когда вы тренируетесь:"
    empty_days_alert = "Выберите хотя бы один день!"
    ask_notes = "Расскажите немного о себе: уровень подготовки, предпочтения и т.д."
    registration_success = "✅ Регистрация завершена. Добро пожаловать в клуб! 💪"
    registration_invalid_data = "❌ Регистрационная форма содержит неверные данные. Пожалуйста, попробуйте еще раз."
    registration_backend_error = (
        "🚧 Не удалось сохранить ваши данные. Пожалуйста, попробуйте еще раз позже."
    )
    registration_backend_unavailable = (
        "⚠️ Сервер сейчас недоступен. Пожалуйста, попробуйте еще раз позже."
    )


class LoginMessages:
    ask_code = "🔑 Введите один из резервных кодов, выданный при регистрации."
    invalid_code = "❌ Неверный код или ошибка. Попробуйте ещё раз."


class BackupCodeMessages:
    title = "<b>🔑 Коды для входа с других аккаунтов</b>"
    item = "{idx}. <code>{code}</code>"
    footer = "<b>⚠️ Сохраните эти коды</b>, это сообщение будет удалено через 60 секунд. Новые коды вы сможете сгенерировать командой /backup_codes"

    @classmethod
    def full(cls, codes: list[str]) -> str:
        lines = [cls.item.format(idx=i + 1, code=code) for i, code in enumerate(codes)]
        return "\n".join([cls.title, *lines, "", cls.footer])


class StartMessages:
    welcome_registered = "👋 Привет, {name}!\nВы в главном меню."
    welcome_unregistered = "👋 Привет! Похоже, вы ещё не зарегистрированы."


class SettingsMessages:
    settings_title = "⚙️ Настройки"
    profile_not_found = "❌ Профиль не найден. Пройдите регистрацию."
    profile_view = (
        "<b>👤 Профиль</b>\n"
        "ФИО: {full_name}\n"
        "Возраст: {age}\n"
        "Вес: {weight} кг\n"
        "Рост: {height} см\n"
        "Цель: {goal}\n"
        "Место тренировок: {training_place}\n"
        "Время: {training_time}\n"
        "Дни: {training_days}\n"
    )


class ErrorMessages:
    unknown = "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже."
    backend_unavailable = "⚠️ Сервер сейчас недоступен. Пожалуйста, попробуйте позже."
    backend_error = "🚧 Ошибка при сохранении данных. Повторите попытку позже."
