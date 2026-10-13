#!/usr/bin/env bash
# Build only the SDK's pages of the platform's Sphinx docs, in a temporary directory, and report
# their warnings. It takes seconds, unlike the platform's full build. Warnings about links to pages
# outside the SDK's section ("unknown document") are expected, and left out.
#
# usage, from the smarter-python repository root:
#   skills/smarter-sphinx-docs/scripts/check-sdk-pages.sh [path of a smarter checkout, default ../smarter]
set -euo pipefail

SMARTER="${1:-../smarter}"
SOURCE="$SMARTER/docs/source/smarter-framework"
SPHINX="$SMARTER/venv/bin/python"
[ -x "$SPHINX" ] || SPHINX=python3

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/src/smarter-framework"
cp "$SOURCE/smarter-python.rst" "$WORK/src/smarter-framework/"
cp -R "$SOURCE/smarter-python" "$WORK/src/smarter-framework/"
printf 'project = "smarter-python"\nextensions = []\nroot_doc = "smarter-framework/smarter-python"\n' > "$WORK/src/conf.py"

"$SPHINX" -m sphinx -q -b html "$WORK/src" "$WORK/out" > "$WORK/log.txt" 2>&1 || true
warnings=$(grep -v "unknown document" "$WORK/log.txt" | sed "s#$WORK/src/##" || true)
if [ -n "$warnings" ]; then
  echo "$warnings"
  exit 1
fi
echo "ok"
