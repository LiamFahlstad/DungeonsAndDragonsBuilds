"""List the Rules Glossary entries that code (or any text) mentions, so you know which ones to read.

Usage (from the repo root):
    python .claude/skills/rules-glossary/glossary_terms.py CharacterContent/Features/CharacterFeats/GeneralFeats.py
    python .claude/skills/rules-glossary/glossary_terms.py Combat/CombatUIQt/ --lines 10
    python .claude/skills/rules-glossary/glossary_terms.py $(git diff --name-only) --all

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


def source_files(paths: list[Path]) -> list[Path]:
    files = []
    for path in paths:
        if path.is_dir():
            files += [
                p
                for p in sorted(path.rglob("*"))
                if p.suffix in SUFFIXES and p.is_file() and not SKIP_DIRS & set(p.parts)
            ]
        elif path.is_file():
            files.append(path)
        else:
            print(f"skipping {path}: not found", file=sys.stderr)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=Path, help="files or folders to scan")
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
    for path in source_files(args.paths):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        try:
            shown = path.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            shown = path.as_posix()
        for number, line in enumerate(text.splitlines(), start=1):
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
