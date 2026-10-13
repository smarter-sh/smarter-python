#!/usr/bin/env bash
# Run the unit tests with the lowest versions that requirements/base.txt allows, on the lowest
# supported Python, in a throwaway virtual environment. The development venv has the newest
# versions, and leftovers of older requirements, so it can't show that the declared ranges hold.
#
# usage, from the smarter-python repository root:
#   skills/monthly-maintenance/scripts/test-minimum-versions.sh [python, default python3.10]
set -euo pipefail

PYTHON="${1:-python3.10}"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# each "package>=X,<Y" line becomes "package==X"
pins=$(grep -E '^[A-Za-z0-9_.-]+>=' requirements/base.txt | sed -E 's/^([A-Za-z0-9_.-]+)>=([^,; ]+).*/\1==\2/')
echo "Python: $($PYTHON --version)"
echo "minimum versions:"
echo "$pins" | sed 's/^/  /'

"$PYTHON" -m venv "$WORK/venv"
# shellcheck disable=SC2086 # one argument per pin
PYTHONPATH= "$WORK/venv/bin/pip" install --quiet $pins
PYTHONPATH=. "$WORK/venv/bin/python" -m unittest discover -s tests -t .
