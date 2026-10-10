#!/usr/bin/env bash
# Type-check the repo with pyright (standard mode), using the same
# pyrightconfig.json the editor's Pylance reads, so both report the same.
# Usage: ./typecheck.sh            # the whole repo
#        ./typecheck.sh Model      # one folder
#
# Excluded (see pyrightconfig.json): web scrapers run by hand (Scrapers/,
# Combat/Tools/scrape_monsters.py), whose BeautifulSoup lookups the stubs type
# as Optional at every step, and generated scratch output. Install the
# checker with: pip install pyright

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

"$PYTHON" -m pyright "$@"
