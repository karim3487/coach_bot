PROJECT_DIR=coach_bot

all: lint

lint:
	poetry run python -m ruff check $(PROJECT_DIR) --config pyproject.toml --fix
	poetry run python -m isort $(PROJECT_DIR)
	poetry run python -m mypy $(PROJECT_DIR) --config-file pyproject.toml
	poetry run python -m black $(PROJECT_DIR) --config pyproject.toml

schema_build:
	poetry run datamodel-codegen \
	--url 'http://localhost:8000/api/v1/schema' \
	--input-file-type openapi \
	--output coach_bot/models/schemas.py
	./scripts/replace_slug.sh coach_bot/models/schemas.py

init_project:
	poetry run python infra/scripts/init_project.py