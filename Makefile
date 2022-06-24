install:
	poetry install

dev:
	poetry run uvicorn src.main:app --reload

bundle:
	poetry export -f requirements.txt --without-hashes --output src/requirements.txt
	sam build
	cp -r src .aws-sam/build/AppFunction
	cd .aws-sam/build/AppFunction ; zip -r ../../../artifact.zip . -x '*.pyc' -x '*_test.py'

deploy:
	sam deploy

test:
	poetry run pytest

lint:
	poetry run flake8 src/ && poetry run black src/ --check
