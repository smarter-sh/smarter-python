#!/usr/bin/env bash
# Copy the Smarter platform's published api contracts into the SDK's test data.
#
# The SDK mirrors the platform's Pydantic contract models (smarter/models/chat.py and
# smarter/models/journal.py). Its tests check that the mirror declares every field of the
# platform's JSON Schemas, and parses the platform's example of each model. Run this after the
# platform's contracts change, then run the tests.
#
# usage, from the repository root:
#   scripts/sync-contracts.sh [path of a smarter checkout, default ../smarter] [git ref]
#
# With a git ref (e.g. origin/main), the files are read at that ref with git show, without
# changing the checkout. Without one, they are copied from the checkout's working tree.
set -euo pipefail

SMARTER="${1:-../smarter}"
REF="${2:-}"
TARGET="tests/data/contracts"
FILES=(
  "smarter/smarter/apps/prompt/contract/chat-contract.schema.json"
  "smarter/smarter/apps/prompt/contract/chat-contract.example.json"
  "smarter/smarter/lib/journal/contract/journal-contract.schema.json"
)

if [ ! -d "$SMARTER/smarter/smarter/apps/prompt/contract" ]; then
  echo "No smarter checkout at $SMARTER" >&2
  exit 1
fi

mkdir -p "$TARGET"
for file in "${FILES[@]}"; do
  if [ -n "$REF" ]; then
    git -C "$SMARTER" show "$REF:$file" > "$TARGET/$(basename "$file")"
  else
    cp "$SMARTER/$file" "$TARGET/"
  fi
done
VERSION=$(git -C "$SMARTER" describe --tags --always "${REF:-HEAD}" 2>/dev/null || echo "$SMARTER")
echo "Copied the contracts of $VERSION into $TARGET"
