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

.PHONY: init activate build run clean tear-down lint analyze coverage release pre-commit-init pre-commit-run python-init python-activate python-lint python-clean python-test help

# Default target executed when no arguments are given to make.
all: help

# initialize local development environment.
# takes around 5 minutes to complete
init:
	make check-python		# verify Python 3.11 is installed
	make tear-down			# start w a clean environment
	make python-init		# create/replace Python virtual environment and install dependencies
	make pre-commit-init	# install and configure pre-commit

activate:
	./scripts/activate.sh

# complete Docker build. Performs all 13 steps of the build process regardless of current state.
# takes around 4 minutes to complete
build:
	echo "Please implement the build procedure ..."

# run the web application from Docker
# takes around 30 seconds to complete
run:
	echo "Please implement the run procedure ..."

clean:
	make python-clean

# destroy all Docker build and local artifacts
# takes around 1 minute to complete
tear-down:
	make python-clean

# ---------------------------------------------------------
# Code management
# ---------------------------------------------------------

lint:
	make python-lint

analyze:
	cloc . --exclude-ext=svg,json,zip --fullpath --not-match-d=smarter/smarter/static/assets/ --vcs=git

coverage:
	echo "Please implement the coverage procedure ..."

pre-commit-init:
	pre-commit install
	pre-commit autoupdate

pre-commit-run:
	pre-commit run --all-files

release:
	git commit -m "fix: force a new release" --allow-empty && git push



# ---------------------------------------------------------
# Python
# ---------------------------------------------------------
check-python:
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo >&2 "This project requires $(PYTHON) but it's not installed.  Aborting."; exit 1; }

python-init:
	mkdir -p .pypi_cache && \
	make check-python
	make python-clean && \
	npm install && \
	$(PYTHON) -m venv venv && \
	$(ACTIVATE_VENV) && \
	PIP_CACHE_DIR=.pypi_cache $(PIP) install --upgrade pip && \
	PIP_CACHE_DIR=.pypi_cache $(PIP) install -r requirements/local.txt

python-lint:
	make check-python
	make pre-commit-run
	pylint smarter

python-clean:
	rm -rf venv
	find ./smarter/ -name __pycache__ -type d -exec rm -rf {} +

######################
# HELP
######################

help:
	@echo '===================================================================='
	@echo 'init                   - Initialize local and Docker environments'
	@echo 'activate               - activates Python virtual environment'
	@echo 'build                  - Build Docker containers'
	@echo 'run                    - run web application from Docker'
	@echo 'clean                  - delete all local artifacts, virtual environment, node_modules, and Docker containers'
	@echo 'tear-down              - destroy all docker build and local artifacts'
	@echo '<************************** Code Management **************************>'
	@echo 'lint                   - Run all code linters and formatters'
	@echo 'analyze                - Generate code analysis report using cloc'
	@echo 'coverage               - Generate Docker-based code coverage analysis report'
	@echo 'pre-commit-init        - install and configure pre-commit'
	@echo 'pre-commit-run         - runs all pre-commit hooks on all files'
	@echo 'release                - Force a new Github release'
	@echo '<************************** AWS **************************>'
	@echo 'python-init            - Create a Python virtual environment and install dependencies'
	@echo 'python-lint            - Run Python linting using pre-commit'
	@echo 'python-clean           - Destroy the Python virtual environment and remove __pycache__ directories'
	@echo '===================================================================='
