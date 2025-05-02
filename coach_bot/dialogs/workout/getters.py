from random import randrange

from aiogram_dialog import DialogManager

from coach_bot.dialogs.common.utils import get_display_name
from coach_bot.models.schemas import Workout, WorkoutExerciseRead
from coach_bot.utils.constants import MUSCLE_GROUP, EQUIPMENT, LEVEL


def render_exercises(workout: Workout) -> str:
    parts = []

    for i, ex in enumerate(sorted(workout.exercises_list, key=lambda e: e.order), 1):
        name = ex.exercise.name
        sets = ex.sets
        reps = ex.reps
        duration = ex.duration
        rest = ex.rest_interval
        notes = ex.notes

        if sets and reps:
            desc = f"{sets}×{reps}"
        elif duration:
            desc = f"⏱ {duration} сек"
        else:
            desc = "📌 Без деталей"

        line = f"<b>{i}. {name}</b>: {desc}"

        if rest:
            line += f"  🕓 Отдых: {rest} сек"
        if notes:
            line += f"\n   💬 <i>{notes}</i>"

        parts.append(line)

    return "\n".join(parts)


async def render_workout(workout: Workout) -> str:
    return (
        f"📋 <b>{workout.name}</b>\n"
        f"⏱️ <b>Оценка времени:</b> {workout.duration_est} мин\n"
        f"🎯 <b>Уровень:</b> {get_display_name(LEVEL, workout.level.value)}\n"
        f"📦 <b>Упражнений:</b> {len(workout.exercises_list)}\n"
    )


async def workout_getter(dialog_manager: DialogManager, **kwargs):
    workout: Workout = dialog_manager.start_data.get("workout")

    if not workout:
        return {"text": "❌ Не удалось загрузить тренировку."}

    dialog_manager.dialog_data["workout"] = workout

    workout_text = await render_workout(workout)
    exercises_text = render_exercises(workout)

    return {
        "text": (
            "🏋️ <b>Тренировка на сегодня</b>\n\n"
            f"{workout_text}\n"
            f"📋 <b>Упражнения:</b>\n"
            f"{exercises_text}"
        ),
    }


async def exercise_getter(dialog_manager: DialogManager, **kwargs):
    workout: Workout = dialog_manager.dialog_data["workout"]
    index = dialog_manager.dialog_data.get("current_index", 0)
    exercises = workout.exercises_list

    if index >= len(exercises):
        return {
            "text": "🎉 Все упражнения завершены! Отличная работа!",
            "media_url": None,
            "finished": True,
        }

    ex: WorkoutExerciseRead = exercises[index]
    ex_data = ex.exercise

    description_parts = [
        f"<b>Упражнение:</b> {ex_data.name}",
        f"<b>Целевая группа:</b> {get_display_name(MUSCLE_GROUP, ex_data.muscle_group.value)}",
        f"<b>Инвентарь:</b> {get_display_name(EQUIPMENT, ex_data.equipment.value)}",
    ]

    if ex.sets and ex.reps:
        description_parts.append(f"<b>Сеты × Повторы:</b> {ex.sets}×{ex.reps}")
    elif ex.duration:
        description_parts.append(f"<b>⏱ Продолжительность:</b> {ex.duration} сек")

    if ex.rest_interval:
        description_parts.append(f"<b>🕓 Отдых после:</b> {ex.rest_interval} сек")

    if ex.notes:
        description_parts.append(f"<b>💬 Советы:</b>\n{ex.notes}")

    urls = [
        "https://v2.exercisedb.io/image/QrtoxrcB3ZsmBT",
        "https://v2.exercisedb.io/image/nnCTuaNpbNNJeD",
        "https://v2.exercisedb.io/image/kgIUHE725ArSWa",
        "https://v2.exercisedb.io/image/0WW6Dx-BkChZKj",
    ]

    return {
        "text": "\n".join(description_parts),
        # "media_url": ex_data.media_url,
        "media_url": urls[randrange(0, 3)],
        "is_last": index == len(exercises) - 1,
    }
