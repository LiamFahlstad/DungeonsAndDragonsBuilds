#!/usr/bin/env bash
# Run pytest tests for the D&D character sheet builder.
# Usage: ./run_tests.sh                    # run all tests
#        ./run_tests.sh -k builder         # run tests matching "builder"
#        ./run_tests.sh tests/test_definitions.py  # run specific file
#        ./run_tests.sh -x -q              # stop on first failure, quiet output
#
# Finds the first Python with pytest installed and runs it.
# Works from Git Bash or WSL.

set -euo pipefail

cd "$(dirname "$0")"

PYTHON=""
for candidate in python python3 py python.exe py.exe; do
    if command -v "$candidate" >/dev/null 2>&1 \
        && "$candidate" -m pytest --version >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "error: no Python with pytest installed was found. Install it with: pip install pytest" >&2
    exit 1
fi

"$PYTHON" -m pytest "$@"
