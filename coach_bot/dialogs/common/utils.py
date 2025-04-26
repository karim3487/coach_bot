def get_display_name(mapping: list[tuple[str, str]], value: str) -> str:
    return dict(mapping).get(value, value)


def get_display_list(mapping: list[tuple[str, str]], values: list[str]) -> list:
    return [get_display_name(mapping, value) for value in values]
