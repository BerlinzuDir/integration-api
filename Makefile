install:
	poetry install

dev:
	poetry run uvicorn src.main:app --reload

test:
	poetry run pytest

lint:
	poetry run flake8 src/ && poetry run black src/ --check
