.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install:
	poetry install

poetry-to-pip:
	poetry export -f requirements.txt --output requirements.txt --without-hashes --with jus,dev,doc

.PHONY: pip-install
pip-install:
	pip install -r requirements.txt

increment-version: ## Increment the version in pyproject.toml
	poetry run python settings.py

.PHONY: black
black: ## Check against Black code formatter
	poetry run black . --check

.PHONY: black-apply
black-apply: ## Apply Black code formatter
	poetry run black .

.PHONY: flake8
flake8: ## Check against Flake8 style guide enforcement
	poetry run flake8 . --ignore=E501,W503,E203 --exclude=.venv

.PHONY: isort
isort: ## Check import sort order.
	poetry run isort --profile black . --check-only

.PHONY: isort-apply
isort-apply: ## Sort import order.
	poetry run isort --profile black .

.PHONY: autoflake
autoflake: ## Remove unused imports and unused variables
	poetry run autoflake -rc --remove-unused-variables --remove-all-unused-imports .

.PHONY: test
test: ## Run tests
	poetry run python -m pytest -vv . $(PYTEST_ARGS)

format: black-apply flake8 isort-apply autoflake ## Format all files

quality-assurance: black flake8 isort autoflake ## Check quality assurance

run: ## Run the API
	poetry run uvicorn main:app --reload --port=8055

run-sample: ## Run the main script with a model in samples/ directory
	poetry run python sample.py $(sample)