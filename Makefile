SHELL := /bin/bash
include .env
export PATH := /usr/local/bin:$(PATH)
export

ifeq ($(OS),Windows_NT)
    PYTHON := python.exe
    ACTIVATE_VENV := venv\Scripts\activate
	PYTHONPATH := $(shell pwd)
else
    PYTHON := python3.12
    ACTIVATE_VENV := source venv/bin/activate
	PYTHONPATH := $(shell pwd)
endif
PIP := $(PYTHON) -m pip

ifneq ("$(wildcard .env)","")
else
    $(shell cp ./doc/example-dot-env .env)
endif

.PHONY: init activate build run clean lint analyze coverage test test-live sam-models contracts pre-commit-init pre-commit-run python-init python-activate python-test force-release publish-test publish-prod help

# Default target executed when no arguments are given to make.
all: help

# initialize local development environment.
# takes around 5 minutes to complete
init:
	make check-python		# verify Python 3.11 is installed
	make python-init		# create/replace Python virtual environment and install dependencies
	make pre-commit-init	# install and configure pre-commit

activate:
	./scripts/activate.sh

# -------------------------------------------------------------------------
# Destroy all build artifacts and Python temporary files
# -------------------------------------------------------------------------
clean:
	find ./smarter/ -name __pycache__ -type d -exec rm -rf {} + && \
	rm -rf venv .pytest_cache __pycache__ .pytest_cache node_modules && \
	rm -rf build dist smarter.egg-info

# ---------------------------------------------------------
# Code management
# ---------------------------------------------------------

# -------------------------------------------------------------------------
# Run black and pre-commit hooks.
# includes prettier, isort, flake8, pylint, etc.
# -------------------------------------------------------------------------
lint:
	make check-python
	make pre-commit-run
	pylint smarter
	black .

analyze:
	cloc . --exclude-ext=svg,json,zip --fullpath --vcs=git

coverage:
	PYTHONPATH=$(PYTHONPATH) coverage run --rcfile=smarter/.coveragerc -m unittest discover -s tests -t . && \
	coverage report -m --rcfile=smarter/.coveragerc && \
	coverage xml --rcfile=smarter/.coveragerc

pre-commit-init:
	pre-commit install
	pre-commit autoupdate

pre-commit-run:
	pre-commit run --all-files



# ---------------------------------------------------------
# Python
# ---------------------------------------------------------
check-python:
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo >&2 "This project requires $(PYTHON) but it's not installed.  Aborting."; exit 1; }

python-init:
	mkdir -p .pypi_cache && \
	make check-python
	make clean && \
	npm install && \
	$(PYTHON) -m venv venv && \
	$(ACTIVATE_VENV) && \
	PIP_CACHE_DIR=.pypi_cache $(PIP) install --upgrade pip && \
	PIP_CACHE_DIR=.pypi_cache $(PIP) install -r requirements/local.txt

# -------------------------------------------------------------------------
# Run Python unit tests
# -------------------------------------------------------------------------
test:
	PYTHONPATH=$(PYTHONPATH) python -m unittest discover -s tests -t . && \
	python -m setup_test

# -------------------------------------------------------------------------
# Test the SDK against a running Smarter platform, e.g. the local one:
# SMARTER_BASE_URL=http://localhost:9357 SMARTER_API_KEY=... make test-live
# These prompt an LLMClient, which makes billable LLM requests.
# -------------------------------------------------------------------------
test-live:
	PYTHONPATH=$(PYTHONPATH) SMARTER_TEST_LIVE=true python -m unittest discover -s tests/live -t . -v

# -------------------------------------------------------------------------
# Regenerate smarter/models/sam/ from a running platform's JSON Schemas.
# -------------------------------------------------------------------------
sam-models:
	PYTHONPATH=$(PYTHONPATH) python scripts/generate_sam_models.py

# -------------------------------------------------------------------------
# Copy the platform's chat and journal contracts from ../smarter.
# -------------------------------------------------------------------------
contracts:
	scripts/sync-contracts.sh ../smarter

# -------------------------------------------------------------------------
# Build the project
# -------------------------------------------------------------------------
build:
	@echo "-------------------------------------------------------------------------"
	@echo "                   I. Unit tests"
	@echo "-------------------------------------------------------------------------"
	make test
	@echo "-------------------------------------------------------------------------"
	@echo "                   II. Check version"
	@echo "-------------------------------------------------------------------------"
	npx semantic-release --doctor --dry-run
	@echo "-------------------------------------------------------------------------"
	@echo "                   III. Initializing the project,"
	@echo "                        Linting and running pre-commit hooks"
	@echo "-------------------------------------------------------------------------"
	make init
	. venv/bin/activate
	$(PIP) install --upgrade setuptools wheel twine
	$(PIP) install --upgrade build
	@echo "-------------------------------------------------------------------------"
	@echo "                   IV. Building the project"
	@echo "-------------------------------------------------------------------------"
	rm -rf build dist .pytest_cache smarter_api.egg-info
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m build --sdist ./ --no-isolation
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m build --wheel ./

	@echo "-------------------------------------------------------------------------"
	@echo "                   V. Verifying the build"
	@echo "-------------------------------------------------------------------------"
	twine check dist/*

# -------------------------------------------------------------------------
# Force a new semantic release to be created in GitHub
# -------------------------------------------------------------------------
force-release:
	git commit -m "fix: force a new release" --allow-empty && git push

# -------------------------------------------------------------------------
# Publish to PyPi Test
# https://test.pypi.org/project/smarter-api/
# -------------------------------------------------------------------------
publish-test:
	git rev-parse --abbrev-ref HEAD | grep '^main$$' || (echo 'Not on main branch, aborting' && exit 1)
	make build
	twine upload --verbose --skip-existing --repository testpypi dist/*

# -------------------------------------------------------------------------
# Publish to PyPi
# https://pypi.org/project/smarter-api/
# -------------------------------------------------------------------------
publish-prod:
	git rev-parse --abbrev-ref HEAD | grep '^main$$' || (echo 'Not on main branch, aborting' && exit 1)
	make build
	twine upload --verbose --skip-existing dist/*

######################
# HELP
######################

help:
	@echo '===================================================================='
	@echo 'init                   - Initialize local and Docker environments'
	@echo 'activate               - activates Python virtual environment'
	@echo 'clean                  - delete all local artifacts, virtual environment, node_modules, and Docker containers'
	@echo 'python-init            - Create a Python virtual environment and install dependencies'
	@echo 'clean                  - Destroy the Python virtual environment and remove __pycache__ directories'
	@echo '<************************** Code Management **************************>'
	@echo 'lint                   - Run all code linters and formatters'
	@echo 'analyze                - Generate code analysis report using cloc'
	@echo 'coverage               - run the unit tests with a coverage report'
	@echo 'pre-commit-init        - install and configure pre-commit'
	@echo 'pre-commit-run         - runs all pre-commit hooks on all files'
	@echo '<************************** CI/CD **************************>'
	@echo 'test			- run Python unit tests'
	@echo 'test-live		- test against a running Smarter platform (SMARTER_BASE_URL, SMARTER_API_KEY)'
	@echo 'sam-models		- regenerate the SAM models from a running platform'
	@echo 'contracts		- copy the chat and journal api contracts from ../smarter'
	@echo 'build			- build the project'
	@echo 'force-release		- force a new release to be created in GitHub'
	@echo 'publish-test		- test deployment to PyPi'
	@echo 'publish-prod		- production deployment to PyPi'
	@echo '===================================================================='
