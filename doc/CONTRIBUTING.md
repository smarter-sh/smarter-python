# Developer Setup Guide

[![Python](https://a11ybadges.com/badge?logo=python)](https://www.python.org/)

You should be able to work unencumbered in any of Linux, macOS or Windows. This repository contains five distinct projects, respectively, written in:

- [Python](#python-setup)

In each case there are various technology-specific resources that you'll need to initialize in your development environment. See setup instructions below for each technology.

## Quick Start

```console
git clone https://github.com/smarter-sh/smarter-python.git
make         # scaffold a .env file in the root of the repo
             #
             # ****************************
             # STOP HERE!
             # ****************************
             # Add your Smarter Api key to .env located in the project
             # root folder.

make init    # initialize dev environment, build & init docker.
make build   # builds and configures all docker containers
make run     # runs all docker containers and starts a local web server on port 8000
```

To preserve your own sanity, don't spend time formatting your Python source code because pre-commit invokes automatic code formatting utilities such as black, flake8 and prettier, on all local commits, and these will reformat the code in your commit based on policy configuration files found in the root of this repo.

## Good Coding Best Practices

This project demonstrates a wide variety of good coding best practices for managing mission-critical cloud-based micro services in a team environment, namely its adherence to [12-Factor Methodology](./doc/12-FACTOR.md). Please see this [Code Management Best Practices](./doc/GOOD_CODING_PRACTICE.md) for additional details.

We want to make this project more accessible to students and learners as an instructional tool while not adding undue code review workloads to anyone with merge authority for the project. To this end we've also added several pre-commit code linting and code style enforcement tools, as well as automated procedures for version maintenance of package dependencies, pull request evaluations, and semantic releases.

## Repository Setup

### .env setup

Smarter uses a **LOT** of configuration data. You'll find a pre-formatted quick-start sample .env [here](./example-dot-env) to help you get started, noting however that simply running `make` from the root of this repo will scaffold this exact file for you.

### pre-commit setup

This project uses pre-commit as a first-pass automated code review / QC process. pre-commit runs a multitude of utilities and checks for code formatting, linting, syntax checking, and ensuring that you don't accidentally push something to GitHub which you'd later regret. Broadly speaking, these checks are aimed at minimizing the extent of commits that contain various kinds of defects and stylistic imperfections that don't belong on the main branch of the project.

Note that many of the pre-commit commands are actually executed by Python which in turn is calling pip-installed packages listed in smarter/requirements/local.txt located in the root of the repo. It therefore is important that you first create the Python virtual environment using `make pre-commit`. It also is a good idea to do a complete 'dry run' of pre-commit, to ensure that your developer environment is correctly setup:

```console
make pre-commit
```

Output should look similar to the following:

![pre-commit output](./doc/img/pre-commit.png)

### Github Secrets setup

Common secrets for automated CD/CD processes are managed with [GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions). The GitHub Actions automated processes depend on several of these. When creating pull requests, the GitHub Actions will use these secrets, [github.com/QueriumCorp/smarter/settings/secrets/actions](https://github.com/QueriumCorp/smarter/settings/secrets/actions), so there's nothing special for you to do.

On the other hand, if you've forked this repo and are working on your own independent project, then you'll need to initialize each of these yourself.

![Github Secrets](./doc/img/github-secrets.png)

### GitHub Actions

This project depends heavily on GitHub Actions to automate routine activities, so that hopefully, the source code is always well-documented and easy to read, and everything works perfectly. We automate the following in this project:

- Code style and linting checks, during both pre-commit as well as triggered on pushes to the main branch
- Unit tests for Python, React and Terraform
- Docker builds
- Environment-specific deployments to Kubernetes
- Semantic Version releases
- version bumps from npm, PyPi and Terraform Registry

A typical pull request will look like the following:

![Automated pull request](./doc/img/automated-pr.png)

## Python Setup

Smarter strictly follows generally accepted best practices and coding conventions for both of these. Thus, to work effectively on this project you'll need familiarity with both of these third party code libraries. Also note that this project leverages [Dependabot](https://github.com/dependabot) and [Mergify](https://mergify.com/) for managing version numbers of all Python dependencies that are used in this project. These two services monitor all of the Python (and NPM and Terraform) dependencies for the project, automatically bumping package versions as well as running unit-tests in order to guard the main branch against breaking changes. Versions should therefore always be up to date at the moment that you clone the repo, and it should not be necessary for you to manually bump PyPi package version numbers inside the Python requirements files.

- Python requirements: [requirements](../requirements/).
- Dependabot configuration: [.github/dependabot.yml](../.github/dependabot.yml)
- Mergify configuration: [.mergify.yml](../.mergify.yml)

```console
make init
source venv/bin/activate
```

### Configuration Data

Smarter generally follows Django's convention of storing most configuration data in environment-specific python modules that are accessible via `django.conf.settings`. However, in light of the fact that Smarter uses a **LOT** of configuration data, and that this configuration data necessarily lives in many different locations, we also have our own propriety configuration module which is based on [Pydantic](https://docs.pydantic.dev/). The module can be found [here](../smarter/smarter/apps/common/conf.py) and is accessed as follows:

```python
from smarter.apps.common.conf import settings as smarter_settings
```

### Unit Tests

We're using `unittest` combined with `django.test` in this project. There's a shortcut for running all tests: `make django-test`. You should create relevant unit tests for your new features, sufficient to achieve a [Coverage](https://coverage.readthedocs.io/) analysis of at least 75%.

### Coverage

Coverage.py is a tool for measuring code coverage of Python programs. It monitors your program, noting which parts of the code have been executed, then analyzes the source to identify code that could have been executed but was not.

Coverage measurement is typically used to gauge the effectiveness of tests. It can show which parts of your code are being exercised by tests, and which are not.

Note the following shortcut for running a Coverage report: `make coverage`.

**Our goal for this project is to maintain an overall Coverage score of at least 80%.**
