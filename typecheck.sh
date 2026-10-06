#!/usr/bin/env bash
# Type-check the Model package with pyright (basic mode, dev-only).
# Usage: ./typecheck.sh
#
# The config lives in pyright-model.json, not pyrightconfig.json, so it
# doesn't change what Pylance reports in the editor. Install the checker
# with: pip install pyright

set -euo pipefail

cd "$(dirname "$0")"

PYTHON=""
for candidate in python python3 py python.exe py.exe; do
    if command -v "$candidate" >/dev/null 2>&1 \
        && "$candidate" -m pyright --version >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "error: no Python with pyright installed was found. Install it with: pip install pyright" >&2
    exit 1
fi

"$PYTHON" -m pyright -p pyright-model.json "$@"
