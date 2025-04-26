from aiogram_dialog.widgets.text import Multi, Const, Format

profile_text = Multi(
    Const("📝 Пожалуйста, проверьте введённые данные:"),
    Format("Имя: {name}"),
    Format("Возраст: {age}"),
    Format("Вес: {weight} кг"),
    Format("Рост: {height} см"),
    Format("Пол: {gender}"),
    Format("Место тренировок: {training_location}"),
    Format("Доступные дни: {available_days}"),
    Format("Время тренировок: {preferred_time}"),
    Format("Цель: {goal_display}"),
    sep="\n",
)
