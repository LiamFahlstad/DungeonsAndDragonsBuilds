"""List the Rules Glossary entries that code (or any text) mentions, so you know which ones to read.

Usage (from the repo root):
    python .claude/skills/rules-glossary/glossary_terms.py CharacterContent/Features/CharacterFeats/GeneralFeats.py
    python .claude/skills/rules-glossary/glossary_terms.py Combat/CombatUIQt/ --lines 10
    python .claude/skills/rules-glossary/glossary_terms.py $(git diff --name-only) --all
    python .claude/skills/rules-glossary/glossary_terms.py CharacterContent/Features/CharacterFeats/OriginFeats.py::TavernBrawler
    python .claude/skills/rules-glossary/glossary_terms.py CharacterContent/Features/CharacterFeats/GeneralFeats.py:602-639

A whole feature file names entries for every feature in it, so for one feature pass
`file.py::ClassName` (the class or def, up to the next line indented as little) or a line range.

Matching is case-insensitive on whole words, after splitting identifiers into words, so
`BonusAction`, `bonus_action` and "Bonus Action" all match the Bonus Action entry, and
`Condition.GRAPPLED` matches Grappled. A trailing "s" is allowed ("Opportunity Attack").
Terms too common to be useful on their own (Creature, Target, Damage, ...) are summed up on
one line unless --all is given. Entries come from the generated tree's own headings, so the
script never goes stale; if the tree is missing, generate it with scrape_rules_glossary.py.
"""

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
DEFAULT_GLOSSARY = REPO_ROOT / "SourceTexts" / "RulesGlossary"
SUFFIXES = {".py", ".json", ".md", ".txt"}
SKIP_DIRS = {"__pycache__", ".git", ".claude", "Output"}

# Entries whose names are everyday words in this codebase; a match says little on its own.
GENERIC = {
    "Action",
    "Adventure",
    "Ally",
    "Campaign",
    "Creature",
    "Damage",
    "Dead",
    "Encounter",
    "Enemy",
    "Healing",
    "Monster",
    "Object",
    "Proficiency",
    "Reach",
    "Save",
    "Size",
    "Skill",
    "Speed",
    "Spell",
    "Target",
    "Weapon",
}

# Tagged entries whose bare name is an everyday word: only "<name> <tag>" counts ("Magic action",
# "Hide action"), since "magic" or "attack" alone is in nearly every feature.
NEEDS_TAG = {
    "Attack",
    "Help",
    "Hide",
    "Influence",
    "Line",
    "Magic",
    "Ready",
    "Search",
    "Study",
    "Utilize",
}

TAG_RE = re.compile(r"\s*\[(?P<tag>[^\]]+)\]$")


def load_entries(glossary: Path) -> dict[str, tuple[str, str]]:
    """{entry name without its tag: (path relative to the glossary root, phrase to match)}"""
    entries = {}
    for path in sorted(glossary.rglob("*.md")):
        if path.name == "index.md":
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                match = TAG_RE.search(title)
                name = TAG_RE.sub("", title)
                phrase = (
                    f"{name} {match['tag']}" if match and name in NEEDS_TAG else name
                )
                entries[name] = (path.relative_to(glossary).as_posix(), phrase)
                break
    return entries


def words(line: str) -> str:
    """Split identifiers into words: 'Condition.GRAPPLED' -> 'condition grappled'."""
    line = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", line)
    return re.sub(r"[_.\-]+", " ", line).lower()


def term_pattern(name: str) -> re.Pattern:
    parts = [re.escape(part) for part in words(name).split()]
    return re.compile(r"\b" + r"\s+".join(parts) + r"s?\b")


SCOPE_RE = re.compile(
    r"^(?P<path>.+?)(?::(?P<start>\d+)-(?P<end>\d+)|::(?P<symbol>\w+))?$"
)


def symbol_range(lines: list[str], symbol: str) -> tuple[int, int] | None:
    """1-based line range of `class symbol` or `def symbol`: up to the next line indented as little."""
    pattern = re.compile(rf"^(?P<indent>\s*)(?:async\s+)?(?:class|def)\s+{symbol}\b")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            indent = len(match["indent"])
            end = index + 1
            while end < len(lines) and (
                not lines[end].strip()
                or len(lines[end]) - len(lines[end].lstrip()) > indent
            ):
                end += 1
            while end > index + 1 and not lines[end - 1].strip():
                end -= 1
            return index + 1, end
    return None


def source_scopes(args: list[str]) -> list[tuple[Path, str | None]]:
    """[(file, "START-END" or "::Symbol" or None)] for files, folders and file scopes."""
    scopes: list[tuple[Path, str | None]] = []
    for arg in args:
        match = SCOPE_RE.match(arg)
        assert match
        path = Path(match["path"])
        scope = (
            f"{match['start']}-{match['end']}"
            if match["start"]
            else match["symbol"] and "::" + match["symbol"]
        )
        if path.is_dir() and not scope:
            scopes += [
                (p, None)
                for p in sorted(path.rglob("*"))
                if p.suffix in SUFFIXES and p.is_file() and not SKIP_DIRS & set(p.parts)
            ]
        elif path.is_file():
            scopes.append((path, scope))
        else:
            print(f"skipping {arg}: not found", file=sys.stderr)
    return scopes


def scoped_lines(path: Path, scope: str | None) -> list[tuple[int, str]] | None:
    """[(line number, line)] inside the scope, or None (with a message) if it can't be read."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return None
    if scope is None:
        start, end = 1, len(lines)
    elif scope.startswith("::"):
        found = symbol_range(lines, scope[2:])
        if found is None:
            print(
                f"skipping {path}{scope}: no class or def by that name", file=sys.stderr
            )
            return None
        start, end = found
    else:
        start, end = (int(n) for n in scope.split("-"))
    return [(n, lines[n - 1]) for n in range(start, min(end, len(lines)) + 1)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="+",
        help="files or folders to scan; file.py:START-END or file.py::ClassOrFunction scans part of a file",
    )
    parser.add_argument(
        "--glossary",
        type=Path,
        default=DEFAULT_GLOSSARY,
        help="the generated glossary tree",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="list generic terms (Creature, Damage, ...) in full too",
    )
    parser.add_argument(
        "--lines", type=int, default=5, help="line numbers to show per file (default 5)"
    )
    args = parser.parse_args()

    if not args.glossary.is_dir():
        print(
            f"No glossary at {args.glossary}; run scrape_rules_glossary.py first.",
            file=sys.stderr,
        )
        return 2
    entries = load_entries(args.glossary)
    patterns = {name: term_pattern(phrase) for name, (_, phrase) in entries.items()}

    # name -> file -> line numbers
    hits: dict[str, dict[str, list[int]]] = {}
    for path, scope in source_scopes(args.paths):
        numbered = scoped_lines(path, scope)
        if numbered is None:
            continue
        try:
            shown = path.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            shown = path.as_posix()
        for number, line in numbered:
            normalized = words(line)
            for name, pattern in patterns.items():
                if pattern.search(normalized):
                    hits.setdefault(name, {}).setdefault(shown, []).append(number)

    def total(name: str) -> int:
        return sum(len(lines) for lines in hits[name].values())

    specific = sorted(
        (n for n in hits if args.all or n not in GENERIC), key=lambda n: (-total(n), n)
    )
    generic = sorted(
        (n for n in hits if not args.all and n in GENERIC), key=lambda n: (-total(n), n)
    )
    if not hits:
        print("No glossary terms found.")
        return 0
    width = max(len(entries[n][0]) for n in specific) if specific else 0
    for name in specific:
        print(f"{entries[name][0]:<{width}}  {total(name):>4}")
        for shown, lines in hits[name].items():
            more = f" (+{len(lines) - args.lines})" if len(lines) > args.lines else ""
            print(f"    {shown}:{','.join(map(str, lines[: args.lines]))}{more}")
    if generic:
        print(
            "generic (--all to list): " + ", ".join(f"{n} {total(n)}" for n in generic)
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
