from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets import kbd
from aiogram_dialog.widgets import text
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.media import StaticMedia

from coach_bot.dialogs.common.widgets.buttons import back_button
from coach_bot.dialogs.workout import handlers
from coach_bot.dialogs.workout.getters import workout_getter, exercise_getter
from coach_bot.states.user import UserWorkout, UserMainMenu

workout_dialog = Dialog(
    Window(
        text.Const("🛌 Сегодня тренировок нет. Восстановление — тоже часть плана 💆"),
        kbd.Row(
            kbd.Start(text.Const("⬅️ Назад в меню"), id="to_menu", state=UserMainMenu.menu),
        ),
        state=UserWorkout.no_workout,
    ),
    Window(
        text.Format(
            "{text}",
        ),
        kbd.Row(
            kbd.Button(text.Const("🚀 Начать тренировку"), id="start", on_click=handlers.start_exercise),
            kbd.Start(text.Const("⬅️ Назад"), id="back", state=UserMainMenu.menu),
        ),
        state=UserWorkout.overview,
        getter=workout_getter,
    ),
    Window(
        text.Format("{text}"),
        StaticMedia(url=text.Format("{media_url}"), type=ContentType.ANIMATION),
        kbd.Column(
            kbd.Button(text.Const("📝 Отметить результат"), id="record", on_click=handlers.on_record_result),
            kbd.Button(text.Const("➡️ Продолжить"), id="next", on_click=handlers.next_exercise),
        ),
        state=UserWorkout.exercise,
        getter=exercise_getter,
    ),
    Window(
        text.Const("🔁 Сколько повторений вы выполнили?"),
        back_button,
        MessageInput(handlers.on_reps_entered),
        state=UserWorkout.enter_reps,
    ),

    Window(
        text.Const("🏋️ Введите вес в килограммах (если вы выполняли с собственным весом введите 0):"),
        back_button,
        MessageInput(handlers.on_weight_entered),
        state=UserWorkout.enter_weight,
    ),
    Window(
        text.Const("⏱ Сколько секунд вы выполняли упражнение?"),
        back_button,
        MessageInput(handlers.on_duration_entered),
        state=UserWorkout.enter_duration,
    ),
    Window(
        text.Const("📝 Хотите оставить заметку к этому упражнению?\n"
                   "Например: 'Было тяжело', 'Следующий раз +2 кг'.\n"
                   'Или отправьте "-", чтобы пропустить.'),
        MessageInput(handlers.on_note_entered),
        state=UserWorkout.enter_note,
    ),
)
