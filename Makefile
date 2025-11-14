# -----------------------------------------------------------------------------
# Makefile
# -----------------------------------------------------------------------------

# Use a predictable shell; make each recipe run in one shell; fail fast.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

.DEFAULT_GOAL := init

# -----------------------------------------------------------------------------
# Python and virtual environment related
# -----------------------------------------------------------------------------

# Prefer an explicit 3.12, falling back sanely.
BASE_PYTHON := $(shell command -v /opt/homebrew/bin/python3.12 || command -v python3.12 || command -v python3)

ifdef VIRTUAL_ENV
VENV_DIR := $(VIRTUAL_ENV)
else ifdef venv
VENV_DIR := $(venv)
else
VENV_DIR := ./.venv
endif

PYTHON := $(VENV_DIR)/bin/python
PIP    := $(VENV_DIR)/bin/pip

create-venv:
	# Create venv and upgrade packaging tools.
	"$(BASE_PYTHON)" -m venv "$(VENV_DIR)"
	"$(PYTHON)" -m pip install --upgrade pip setuptools wheel

init: create-venv
	# Install base requirements into venv.
	#"$(PIP)" install -r requirements.in
	"$(PIP)" install -e .'[all]'

install: init
	# Install developer hooks without leaving a dangling backslash.
	. "$(VENV_DIR)/bin/activate"
	pre-commit autoupdate
	pre-commit install --hook-type pre-push --hook-type post-checkout --hook-type pre-commit

install-dev: create-venv
	# Install any dev-only extras here (optional).
	. "$(VENV_DIR)/bin/activate"
	# Example: "$(PIP)" install -r requirements-dev.in

# -----------------------------------------------------------------------------
# Config, env vars and credentials
# -----------------------------------------------------------------------------
# Pull from environment if present; stay overridable via CLI (e.g., `make run MODEL_NAME=foo`).

PROJECT_ID                  ?= $(shell printf '%s' "$$PROJECT_ID")
MODEL_NAME                  ?= $(shell printf '%s' "$$MODEL_NAME")
OPENAI_API_KEY              ?= $(shell printf '%s' "$$OPENAI_API_KEY")
OPENAI_BASE_URL             ?= $(shell printf '%s' "$$OPENAI_BASE_URL")
GOOGLE_CLIENT_ID            ?= $(shell printf '%s' "$$GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET        ?= $(shell printf '%s' "$$GOOGLE_CLIENT_SECRET")
SECRET_KEY                  ?= $(shell printf '%s' "$$SECRET_KEY")
DISABLE_HTTPS_ENFORCEMENT   ?= $(shell printf '%s' "$$DISABLE_HTTPS_ENFORCEMENT")
INPUT_PATH                  ?= $(shell printf '%s' "$$INPUT_PATH")
OUTPUT_PATH                 ?= $(shell printf '%s' "$$OUTPUT_PATH")
STORAGE_SERVICE_ACCOUNT_B64 ?= $(shell printf '%s' "$$STORAGE_SERVICE_ACCOUNT_B64")
STORAGE_SERVICE_ACCOUNT     ?= $(shell printf '%s' "$$STORAGE_SERVICE_ACCOUNT")
MEDIA_PATH                  ?= $(shell printf '%s' "$$MEDIA_PATH")

SERVICE_NAME := ai-storyteller-2025
REGION       := europe-west4
CONNECTOR_NAME :=
SUBNET_NAME    := app-tier-eu-west4

# Export once so every recipe inherits these (no per-line exports or backgrounding).
export PROJECT_ID MODEL_NAME OPENAI_API_KEY OPENAI_BASE_URL \
       GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET SECRET_KEY \
       DISABLE_HTTPS_ENFORCEMENT INPUT_PATH OUTPUT_PATH \
       STORAGE_SERVICE_ACCOUNT_B64 STORAGE_SERVICE_ACCOUNT \
       STORYTELLER_MEDIA_ROOT, STORYTELLER_MEDIA_PATH STORYTELLER_MEDIA_URL \
       DISABLE_AUTHENTICATION STORYTELLER_OUTPUT_PATH \
       STORYTELLER_OUTPUT_MEDIA_URL

# -----------------------------------------------------------------------------
# Running locally using Python from virtualenv
# -----------------------------------------------------------------------------

# Run the app with env vars applied and a clean Python env.
run:
	# Unset Python env poisons for safety; force venv python.
	PYTHONHOME= PYTHONPATH=
	. "$(VENV_DIR)/bin/activate"
	exec "$(PYTHON)" main.py

shell:
	PYTHONHOME= PYTHONPATH=
	. "$(VENV_DIR)/bin/activate"
	exec "$(VENV_DIR)/bin/ipython"

notebook:
	PYTHONHOME= PYTHONPATH=
	. "$(VENV_DIR)/bin/activate"
	exec "$(VENV_DIR)/bin/marimo" edit --headless --no-token --port 2718 --host 0.0.0.0

mcp:
	/Users/me/.virtualenvs/storyteller/bin/python /Users/me/repos/storyteller-dev/src/storyteller/modules/st/mcp_impl.py http

chat:
	PYTHONHOME= PYTHONPATH=
	. "$(VENV_DIR)/bin/activate"
	exec "storyteller-chat"

tool: chat

# -----------------------------------------------------------------------------
# Docker and deployment
# -----------------------------------------------------------------------------

docker-build:
	# docker compose picks up exported env from make's process environment.
	docker compose build

docker-compose-up:
	docker compose up

docker-compose-up-build:
	docker compose up --build

clean-docker:
	# Remove a specific container if present; ignore errors if missing.
	docker rm -f playground || true

docker-run: clean-docker
	# Run a local container mirroring Cloud Run env.
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

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

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

clean-venv:
	rm -rf "$(VENV_DIR)"

# -----------------------------------------------------------------------------
# Dev handy
# -----------------------------------------------------------------------------

create-secrets:
	. "$(VENV_DIR)/bin/activate"
	detect-secrets scan > .secrets.baseline

detect-secrets:
	. "$(VENV_DIR)/bin/activate"
	detect-secrets scan --baseline .secrets.baseline

pre-commit:
	pre-commit run --all-files

test:
	. "$(VENV_DIR)/bin/activate"
	exec "$(VENV_DIR)/bin/pytest" test_docs.py

doctor:
	# Quick sanity check of interpreter provenance and stdlib.
	PYTHONHOME= PYTHONPATH=
	. "$(VENV_DIR)/bin/activate"
	which python
	python -V
	python -c 'import sys, sysconfig, encodings; \
print("exe:", sys.executable); \
print("base:", getattr(sys, "_base_executable", None)); \
print("prefix:", sys.prefix); \
print("stdlib:", sysconfig.get_paths().get("stdlib"))'

# -----------------------------------------------------------------------------
# Documentation (Sphinx)
# -----------------------------------------------------------------------------

SPHINXOPTS  ?=
SPHINXBUILD := $(VENV_DIR)/bin/sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

serve-docs:
	"$(PYTHON)" -m http.server 5001 --directory "_build/$(filter-out $@,$(MAKECMDGOALS))/"

# Catch-all target: route unknown targets to Sphinx "make mode".
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# -----------------------------------------------------------------------------
# PyPI
# -----------------------------------------------------------------------------

build:
	# Unset Python env poisons for safety; force venv python.
	PYTHONHOME= PYTHONPATH=
	source "$(VENV_DIR)/bin/activate" && python -m build .

check-build:
	# Unset Python env poisons for safety; force venv python.
	PYTHONHOME= PYTHONPATH=
	source "$(VENV_DIR)/bin/activate" && twine check dist/*

release:
	# Unset Python env poisons for safety; force venv python.
	PYTHONHOME= PYTHONPATH=
	source "$(VENV_DIR)/bin/activate" && twine upload dist/* --verbose

test-release:
	# Unset Python env poisons for safety; force venv python.
	PYTHONHOME= PYTHONPATH=
	source "$(VENV_DIR)/bin/activate" && twine upload --repository testpypi dist/*

# -----------------------------------------------------------------------------
# Phony declarations
# -----------------------------------------------------------------------------

.PHONY: init create-venv install install-dev run shell notebook \
        docker-build docker-compose-up docker-compose-up-build clean-docker \
        docker-run print-env-vars docker-run-and-build clean clean-build \
        clean-pyc clean-test clean-venv create-secrets detect-secrets \
        pre-commit test doctor help serve-docs
