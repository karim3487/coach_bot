# Базовый образ с Python
FROM python:3.12-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry (через официальный скрипт)
#ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только pyproject.toml и poetry.lock (если есть)
COPY pyproject.toml poetry.lock* /app/

# Устанавливаем зависимости без dev и без интерактивного режима
RUN poetry install

# Копируем остальной код проекта
COPY . /app

# Команда по умолчанию (замени на свою)
CMD ["poetry", "run", "python", "-m", "coach_bot.bot"]
#poetry run python -m coach_bot.bot