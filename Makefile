SHELL := /bin/bash
include .env
export PATH := /usr/local/bin:$(PATH)
export

ifeq ($(OS),Windows_NT)
    PYTHON := python.exe
    ACTIVATE_VENV := venv\Scripts\activate
else
    PYTHON := python3.12
    ACTIVATE_VENV := source venv/bin/activate
endif
PIP := $(PYTHON) -m pip

ifneq ("$(wildcard .env)","")
else
    $(shell cp ./doc/example-dot-env .env)
endif

.PHONY: init activate build run clean lint analyze coverage pre-commit-init pre-commit-run python-init python-activate python-test force-release publish-test publish-prod help

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
	make pre-commit-run --all-files
	pylint smarter
	black .

analyze:
	cloc . --exclude-ext=svg,json,zip --fullpath --vcs=git

coverage:
	echo "Please implement the coverage procedure ..."

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
	python -m unittest discover -s smarter/tests/ && \
	python -m setup_test

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

	$(PYTHON) -m build --sdist ./
	$(PYTHON) -m build --wheel ./

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
	@echo 'coverage               - Generate Docker-based code coverage analysis report'
	@echo 'pre-commit-init        - install and configure pre-commit'
	@echo 'pre-commit-run         - runs all pre-commit hooks on all files'
	@echo '<************************** CI/CD **************************>'
	@echo 'test			- run Python unit tests'
	@echo 'build			- build the project'
	@echo 'force-release		- force a new release to be created in GitHub'
	@echo 'publish-test		- test deployment to PyPi'
	@echo 'publish-prod		- production deployment to PyPi'
	@echo '===================================================================='
