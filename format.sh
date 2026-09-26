#!/usr/bin/env bash
# Run the Black formatter over the whole repo.
# Usage: ./format.sh           # format files in place
#        ./format.sh --check   # only report files that would change (no edits)
#
# Works from Git Bash or WSL: picks the first Python that has Black installed
# (under WSL this falls through to the Windows python.exe).

set -euo pipefail

cd "$(dirname "$0")"

PYTHON=""
for candidate in python python3 py python.exe py.exe; do
    if command -v "$candidate" >/dev/null 2>&1 \
        && "$candidate" -m black --version >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "error: no Python with Black installed was found. Install it with: pip install black" >&2
    exit 1
fi

"$PYTHON" -m black . \
    --extend-exclude '/(\.claude|Output|SourceTexts|__pycache__|\.pytest_cache)/' \
    "$@"
