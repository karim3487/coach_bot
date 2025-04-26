from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Checkbox, ManagedCheckbox, Group
from aiogram_dialog.widgets.text import Const


def update_selection(manager: DialogManager, checkbox: ManagedCheckbox, key: str):
    is_checked = checkbox.is_checked()
    selected = manager.dialog_data.get(key, set())

    if is_checked:
        selected.add(checkbox.widget_id)
    else:
        selected.discard(checkbox.widget_id)

    manager.dialog_data[key] = selected


def build_checkbox_group(data: list[tuple[str, str]], on_change_handler) -> Group:
    return Group(
        *[
            Checkbox(
                Const(f"{label} ✅"),
                id=key,
                on_state_changed=on_change_handler,
                unchecked_text=Const(label),
            )
            for key, label in data
        ],
        width=2,
    )
