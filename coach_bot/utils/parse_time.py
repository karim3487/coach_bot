import re
from datetime import time

MAX_HOURS = 23
MAX_MINUTES = 59


def parse_time(text: str) -> time | None:
    time_pattern = re.compile(r"^(\d{1,2}):(\d{2})$")
    match = time_pattern.match(text.strip())
    if not match:
        return None

    try:
        hours, minutes = map(int, match.groups())

        if not (0 <= hours <= MAX_HOURS):
            return None
        if not (0 <= minutes <= MAX_MINUTES):
            return None

        return time(hour=hours, minute=minutes)

    except ValueError:
        return None

