#!/usr/bin/env bash
# Run the unit tests with the lowest versions that pyproject.toml allows, on the lowest
# supported Python, in a throwaway virtual environment. The development venv has the newest
# versions, and leftovers of older requirements, so it can't show that the declared ranges hold.
#
# usage, from the smarter-python repository root:
#   skills/monthly-maintenance/scripts/test-minimum-versions.sh [python, default python3.10]
set -euo pipefail

PYTHON="${1:-python3.10}"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# each of pyproject.toml's "package>=X,<Y" dependencies becomes "package==X". python3 (3.11 or
# newer, for tomllib) reads the file; $PYTHON runs the tests.
pins=$(python3 -c 'import re, tomllib; [print(re.sub(r"^([A-Za-z0-9_.-]+)>=([^,; ]+).*", r"\1==\2", d)) for d in tomllib.load(open("pyproject.toml", "rb"))["project"]["dependencies"]]')
echo "Python: $($PYTHON --version)"
echo "minimum versions:"
echo "$pins" | sed 's/^/  /'

"$PYTHON" -m venv "$WORK/venv"
# shellcheck disable=SC2086 # one argument per pin
PYTHONPATH= "$WORK/venv/bin/pip" install --quiet $pins "jsonschema>=4.26"
PYTHONPATH=. "$WORK/venv/bin/python" -m unittest discover -s tests -t .
