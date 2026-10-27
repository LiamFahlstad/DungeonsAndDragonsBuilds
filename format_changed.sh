#!/usr/bin/env bash
# Run the Black formatter over changed or given Python files only (format.sh does the whole repo).
# Usage: ./format_changed.sh                # format every changed .py file (staged, unstaged, untracked)
#        ./format_changed.sh --staged       # format the staged .py files and re-stage them (for commits)
#        ./format_changed.sh FILE...        # format these files
#        ./format_changed.sh --check [...]  # only report files that would change (no edits)
#
# --staged refuses a file that also has unstaged changes: Black rewrites the whole file, so
# re-staging it would sneak the unstaged edits into the commit. Stage the whole file first,
# or commit it without formatting.
#
# Uses the same Python discovery and exclusions as format.sh. Works from Git Bash or WSL.

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

# format.sh's exclusions. Either separator: on Windows, Black matches --force-exclude against
# explicitly listed paths with backslashes.
EXCLUDE='(^|[/\\])(\.claude|Output|SourceTexts|__pycache__|\.pytest_cache)[/\\]'
CHECK=()
STAGED=0
FILES=()
for arg in "$@"; do
    case "$arg" in
        --check) CHECK=(--check --diff) ;;
        --staged) STAGED=1 ;;
        *) FILES+=("$arg") ;;
    esac
done

if [ "$STAGED" -eq 1 ]; then
    # Added/copied/modified/renamed files only; a staged deletion has nothing to format.
    mapfile -t FILES < <(git diff --cached --name-only --diff-filter=ACMR -- '*.py')
    mapfile -t PARTIAL < <(git diff --name-only -- '*.py')
    BLOCKED=()
    for f in "${FILES[@]}"; do
        for p in "${PARTIAL[@]}"; do
            [ "$f" = "$p" ] && BLOCKED+=("$f")
        done
    done
    if [ "${#BLOCKED[@]}" -gt 0 ]; then
        echo "error: these staged files also have unstaged changes; formatting would stage those too:" >&2
        printf '  %s\n' "${BLOCKED[@]}" >&2
        exit 1
    fi
elif [ "${#FILES[@]}" -eq 0 ]; then
    mapfile -t FILES < <(
        { git diff --name-only --diff-filter=ACMR -- '*.py'
          git diff --cached --name-only --diff-filter=ACMR -- '*.py'
          git ls-files --others --exclude-standard -- '*.py'; } | sort -u
    )
fi

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "No Python files to format."
    exit 0
fi

# --force-exclude applies the exclusions to explicitly listed files too.
"$PYTHON" -m black --force-exclude "$EXCLUDE" "${CHECK[@]}" -- "${FILES[@]}"

if [ "$STAGED" -eq 1 ] && [ "${#CHECK[@]}" -eq 0 ]; then
    git add -- "${FILES[@]}"
fi
