from datetime import date

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from aiogram import types

from coach_bot.models.schemas import Workout, ProgressCreateByTelegram
from coach_bot.services.coach_api import api_client
from coach_bot.states.user import UserWorkout, UserMainMenu


def on_finish_workout():
    return None


async def start_exercise(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data["current_index"] = 0
    await manager.switch_to(UserWorkout.exercise)


async def next_exercise(callback: types.CallbackQuery, button: Button, manager: DialogManager):
    current_index = manager.dialog_data.get("current_index", 0)
    workout = manager.dialog_data.get("workout")

    if not workout:
        await callback.answer("⚠️ Тренировка не найдена.", show_alert=True)
        await manager.start(UserMainMenu.menu)
        return

    if current_index + 1 >= len(workout.exercises_list):
        await callback.message.answer("🏁 Вы завершили тренировку! Отличная работа!")
        await manager.start(UserMainMenu.menu)
        return

    manager.dialog_data["current_index"] = current_index + 1
    await manager.switch_to(UserWorkout.exercise)


async def on_record_result(callback: types.CallbackQuery, button: Button, manager: DialogManager):
    workout: Workout = manager.dialog_data["workout"]
    index = manager.dialog_data.get("current_index", 0)
    ex = workout.exercises_list[index]

    if ex.sets and ex.reps:
        await manager.switch_to(UserWorkout.enter_reps)
    elif ex.duration:
        await manager.switch_to(UserWorkout.enter_duration)
    else:
        await callback.message.answer("❌ Упражнение без параметров. Пропускаем.")
        await manager.switch_to(UserWorkout.exercise)


async def on_progress_value_entered(
        message: types.Message, _: MessageInput, manager: DialogManager,
):
    try:
        value = float(message.text.replace(",", "."))
        manager.dialog_data["progress_value"] = value
        await message.answer("✅ Значение принято. (Сохраним позже или запросим единицы измерения)")
        await manager.switch_to(UserWorkout.exercise)
    except ValueError:
        await message.answer("❌ Введите число, например: 10 или 12.5")


async def on_reps_entered(message: types.Message, _: MessageInput, manager: DialogManager):
    try:
        reps = int(message.text)
        manager.dialog_data["progress_reps"] = reps
        await manager.switch_to(UserWorkout.enter_weight)
    except ValueError:
        await message.answer("❌ Введите целое число повторений.")


async def on_weight_entered(message: types.Message, _: MessageInput, manager: DialogManager):
    try:
        weight = float(message.text.replace(",", "."))
        reps = manager.dialog_data["progress_reps"]
        manager.dialog_data["progress_metric"] = {
            "metric": "weight",
            "value": weight,
            "units": "kg",
            "notes": f"{reps} reps",
        }
        await manager.switch_to(UserWorkout.enter_note)

    except ValueError:
        await message.answer("❌ Введите число, например 40 или 75.5.")


async def on_duration_entered(message: types.Message, _: MessageInput, manager: DialogManager):
    try:
        duration = int(message.text)
        manager.dialog_data["progress_metric"] = {
            "metric": "duration",
            "value": duration,
            "units": "s",
            "notes": "",
        }
        await manager.switch_to(UserWorkout.enter_note)

    except ValueError:
        await message.answer("❌ Введите количество секунд (целое число).")


async def on_note_entered(message: types.Message, _: MessageInput, manager: DialogManager):
    telegram_id = message.from_user.id
    workout = manager.dialog_data["workout"]
    index = manager.dialog_data["current_index"]
    exercise = workout.exercises_list[index]
    metric_data = manager.dialog_data["progress_metric"]

    note = message.text.strip()
    if note != "-":
        metric_data["notes"] += f" — {note}"

    progress = ProgressCreateByTelegram(
        telegram_id=telegram_id,
        date=date.today(),
        workout=workout.id,
        exercise=exercise.exercise.id,
        metric=metric_data["metric"],
        value=metric_data["value"],
        units=metric_data["units"],
        notes=metric_data["notes"],
    )

    await api_client.save_progress(progress)

    await message.answer("✅ Результат и заметка сохранены.")
    await manager.switch_to(UserWorkout.exercise)
