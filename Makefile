.PHONY: help install sync update-lock \
        test quick-test shell ipython notebook mcp chat tool \
        docker-build docker-compose-up docker-compose-up-build clean-docker \
        docker-run print-env-vars docker-run-and-build \
        clean clean-build clean-pyc clean-test \
        create-secrets detect-secrets pre-commit pre-commit-install \
        build-docs serve-docs \
        build check-build release test-release

SHELL := /bin/bash

UV ?= uv
PYTHON ?= $(UV) run python
PYTEST ?= $(UV) run pytest
RUFF ?= $(UV) run ruff
MYPY ?= $(UV) run mypy
PRE_COMMIT ?= $(UV) run pre-commit
DETECT_SECRETS ?= $(UV) run detect-secrets
TWINE ?= $(UV) run twine
SPHINX_BUILD ?= $(UV) run sphinx-build

SOURCEDIR = .
BUILDDIR = _build
DOCS_PORT = 5001

PROJECT_ID ?= $(shell printf '%s' "$$PROJECT_ID")
MODEL_NAME ?= $(shell printf '%s' "$$MODEL_NAME")
OPENAI_API_KEY ?= $(shell printf '%s' "$$OPENAI_API_KEY")
OPENAI_BASE_URL ?= $(shell printf '%s' "$$OPENAI_BASE_URL")
GOOGLE_CLIENT_ID ?= $(shell printf '%s' "$$GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET ?= $(shell printf '%s' "$$GOOGLE_CLIENT_SECRET")
SECRET_KEY ?= $(shell printf '%s' "$$SECRET_KEY")
DISABLE_HTTPS_ENFORCEMENT ?= $(shell printf '%s' "$$DISABLE_HTTPS_ENFORCEMENT")
INPUT_PATH ?= $(shell printf '%s' "$$INPUT_PATH")
OUTPUT_PATH ?= $(shell printf '%s' "$$OUTPUT_PATH")
STORAGE_SERVICE_ACCOUNT_B64 ?= $(shell printf '%s' "$$STORAGE_SERVICE_ACCOUNT_B64")
STORAGE_SERVICE_ACCOUNT ?= $(shell printf '%s' "$$STORAGE_SERVICE_ACCOUNT")
MEDIA_PATH ?= $(shell printf '%s' "$$MEDIA_PATH")

SERVICE_NAME := ai-storyteller-2025
REGION := europe-west4
CONNECTOR_NAME :=
SUBNET_NAME := app-tier-eu-west4

export PROJECT_ID MODEL_NAME OPENAI_API_KEY OPENAI_BASE_URL \
       GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET SECRET_KEY \
       DISABLE_HTTPS_ENFORCEMENT INPUT_PATH OUTPUT_PATH \
       STORAGE_SERVICE_ACCOUNT_B64 STORAGE_SERVICE_ACCOUNT \
       STORYTELLER_MEDIA_ROOT STORYTELLER_MEDIA_PATH STORYTELLER_MEDIA_URL \
       DISABLE_AUTHENTICATION STORYTELLER_OUTPUT_PATH \
       STORYTELLER_OUTPUT_MEDIA_URL

help:
	@echo "Common targets:"
	@echo "  make install        Sync uv environment with all groups and extras"
	@echo "  make sync           Same as install"
	@echo "  make test           Run pytest"
	@echo "  make quick-test     Run pytest through uv"
	@echo "  make ruff           Run ruff check"
	@echo "  make mypy           Run mypy"
	@echo "  make pre-commit     Run pre-commit hooks"
	@echo "  make build          Build package"

install sync:
	$(UV) sync --all-groups --all-extras

update-lock:
	$(UV) lock --upgrade

test quick-test:
	$(PYTEST)

ipython:
	$(UV) run ipython

notebook:
	$(UV) run marimo edit --headless --no-token --port 2718 --host 0.0.0.0

mcp:
	$(UV) run python src/storyteller/modules/st/mcp_impl.py http

chat tool:
	$(UV) run storyteller-chat

shell:
	$(UV) run bash

docker-build:
	docker compose build

docker-compose-up:
	docker compose up

docker-compose-up-build:
	docker compose up --build

clean-docker:
	docker rm -f playground || true

docker-run: clean-docker
	docker run \
		--name playground \
		-p 8000:8000 \
		-e OPENAI_API_KEY="$(OPENAI_API_KEY)" \
		-e OPENAI_BASE_URL="$(OPENAI_BASE_URL)" \
		-e MODEL_NAME="$(MODEL_NAME)" \
		-e GOOGLE_CLIENT_ID="$(GOOGLE_CLIENT_ID)" \
		-e GOOGLE_CLIENT_SECRET="$(GOOGLE_CLIENT_SECRET)" \
		-e SECRET_KEY="$(SECRET_KEY)" \
		-e DISABLE_HTTPS_ENFORCEMENT="$(DISABLE_HTTPS_ENFORCEMENT)" \
		-e INPUT_PATH="$(INPUT_PATH)" \
		-e OUTPUT_PATH="$(OUTPUT_PATH)" \
		-e STORAGE_SERVICE_ACCOUNT_B64="$(STORAGE_SERVICE_ACCOUNT_B64)" \
		-e STORAGE_SERVICE_ACCOUNT="$(STORAGE_SERVICE_ACCOUNT)" \
		-e MEDIA_PATH=/app/output \
		-v ./output:/app/output:rw \
		--entrypoint "/app/entrypoint.sh" \
		playground-marimo

print-env-vars:
	@printf "PROJECT_ID: %s\nMODEL_NAME: %s\nOPENAI_API_KEY: %s\nOPENAI_BASE_URL: %s\nGOOGLE_CLIENT_ID: %s\nGOOGLE_CLIENT_SECRET: %s\nSECRET_KEY: %s\nDISABLE_HTTPS_ENFORCEMENT: %s\nINPUT_PATH: %s\nOUTPUT_PATH: %s\nSTORAGE_SERVICE_ACCOUNT_B64: %s\nSTORAGE_SERVICE_ACCOUNT: %s\nMEDIA_PATH: %s\n" \
	"$(PROJECT_ID)" "$(MODEL_NAME)" "$(OPENAI_API_KEY)" "$(OPENAI_BASE_URL)" \
	"$(GOOGLE_CLIENT_ID)" "$(GOOGLE_CLIENT_SECRET)" "$(SECRET_KEY)" \
	"$(DISABLE_HTTPS_ENFORCEMENT)" "$(INPUT_PATH)" "$(OUTPUT_PATH)" \
	"$(STORAGE_SERVICE_ACCOUNT_B64)" "$(STORAGE_SERVICE_ACCOUNT)" "$(MEDIA_PATH)"

docker-run-and-build: docker-build docker-run

clean: clean-build clean-pyc clean-test

clean-build:
	rm -rf build/ dist/ .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.py,cover' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -f .coverage coverage.xml
	rm -rf htmlcov/ .pytest_cache .mypy_cache .ruff_cache

create-secrets:
	$(DETECT_SECRETS) scan > .secrets.baseline

detect-secrets:
	$(DETECT_SECRETS) scan --baseline .secrets.baseline

pre-commit-install:
	$(PRE_COMMIT) install --hook-type pre-push --hook-type post-checkout --hook-type pre-commit

pre-commit: pre-commit-install
	$(PRE_COMMIT) run --all-files

ruff:
	$(RUFF) check .

ruff-fix:
	$(RUFF) check . --fix

format:
	$(RUFF) format .

mypy:
	$(UV) run mypy src

build-docs:
	$(SPHINX_BUILD) -n -b html $(SOURCEDIR) $(BUILDDIR)

serve-docs:
	cd $(BUILDDIR) && $(PYTHON) -m http.server $(DOCS_PORT)

build:
	$(PYTHON) -m build .

check-build:
	$(TWINE) check dist/*

release:
	$(TWINE) upload dist/* --verbose

test-release:
	$(TWINE) upload --repository testpypi dist/* --verbose
