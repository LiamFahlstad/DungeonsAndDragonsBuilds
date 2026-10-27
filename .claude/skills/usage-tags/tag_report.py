"""Where usage_tags are, whether they're valid, and how similar things were tagged.

Usage (from the repo root):
    python .claude/skills/usage-tags/tag_report.py check                 # validate every tag (exit 1 on a problem)
    python .claude/skills/usage-tags/tag_report.py file <path.py> ...     # each feature in these files and its tags
    python .claude/skills/usage-tags/tag_report.py with buff control      # features/spells tagged with all of these
    python .claude/skills/usage-tags/tag_report.py spells --untagged [--level N] [--class Wizard]
                                                                         # spells that render untagged, and the file to tag them in
    python .claude/skills/usage-tags/tag_report.py set-spell "Fireball" damage   # write a spell's tags (--clear removes them)

Features carry usage_tags=[...] in their __init__ call (found here by parsing the code, not
importing it). Spells carry them in CharacterContent/Spells/spells_<source>_extended.json, which
SpellFactory merges over the source record; this tool resolves the same merge, so "untagged"
means "renders with no chips".
"""

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TAGS = ("heal", "buff", "control", "damage", "utility", "summon")
FEATURE_DIR = ROOT / "CharacterContent"
SPELL_DIR = ROOT / "CharacterContent" / "Spells"
# SpellFactory.json_paths, highest priority first: the first source holding a spell wins.
SPELL_SOURCES = ("spells_dnd2024", "spells_aidedd", "spells_dnd5e")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def feature_tags(paths=None) -> list[dict]:
    """Every class whose own __init__ call passes a literal usage_tags list, plus untagged
    classes in explicitly requested files (so `file` can show what's missing)."""
    files = paths or sorted(FEATURE_DIR.rglob("*.py"))
    found = []
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            tags, line = None, cls.lineno
            for call in ast.walk(cls):
                if not isinstance(call, ast.Call):
                    continue
                kw = next((k for k in call.keywords if k.arg == "usage_tags"), None)
                if kw is not None and isinstance(kw.value, ast.List):
                    tags = [e.value if isinstance(e, ast.Constant) else ast.unparse(e) for e in kw.value.elts]
                    line = kw.value.lineno
                    break
            if tags is not None or paths:
                found.append({"name": cls.name, "where": f"{rel(path)}:{line}", "tags": tags})
    return found


def spell_tags() -> list[dict]:
    """The record SpellFactory renders for each spell name, with its tags and the file they live in."""
    spells, seen = [], set()
    for source in SPELL_SOURCES:
        data = json.loads((SPELL_DIR / f"{source}.json").read_text(encoding="utf-8"))
        ext_path = SPELL_DIR / f"{source}_extended.json"
        extended = json.loads(ext_path.read_text(encoding="utf-8")) if ext_path.exists() else {}
        for name, record in data.items():
            if name in seen:
                continue  # a higher-priority source already supplies this spell
            seen.add(name)
            tags = extended.get(name, {}).get("usage_tags", record.get("usage_tags"))
            spells.append({
                "name": name, "where": rel(ext_path), "tags": tags,
                "level": record.get("level"), "classes": record.get("classes") or [],
                "shadowed_source_tags": "usage_tags" in record,
            })
    return spells


def problems_in(items: list[dict], kind: str) -> list[str]:
    problems = []
    for item in items:
        tags = item["tags"]
        if tags is None:
            continue
        label = f"{kind} {item['name']} ({item['where']})"
        if not tags:
            problems.append(f"{label}: empty list; omit usage_tags instead")
        bad = [t for t in tags if t not in TAGS]
        if bad:
            problems.append(f"{label}: unknown tag(s) {bad}; allowed: {', '.join(TAGS)}")
        if len(set(tags)) != len(tags):
            problems.append(f"{label}: duplicate tag in {tags}")
        if item.get("shadowed_source_tags"):
            problems.append(f"{label}: usage_tags in the source JSON are overridden by {item['where']}; move them there")
    return problems


def cmd_check(_args) -> int:
    features, spells = feature_tags(), spell_tags()
    problems = problems_in(features, "feature") + problems_in(spells, "spell")
    for kind, items in (("features", features), ("spells", spells)):
        tagged = [i for i in items if i["tags"]]
        counts = {t: sum(t in i["tags"] for i in tagged) for t in TAGS}
        print(f"{kind}: {len(tagged)} tagged" + (f" of {len(items)}" if kind == "spells" else "")
              + "  (" + ", ".join(f"{t} {n}" for t, n in counts.items()) + ")")
    for problem in problems:
        print(f"  PROBLEM  {problem}")
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_file(args) -> int:
    paths = [Path(p).resolve() for p in args.paths]
    for item in feature_tags(paths):
        tags = ", ".join(item["tags"]) if item["tags"] else "-"
        print(f"  {item['name']:<40} {tags:<28} {item['where']}")
    return 0


def cmd_with(args) -> int:
    wanted = set(args.tags)
    unknown = wanted - set(TAGS)
    if unknown:
        print(f"unknown tag(s) {sorted(unknown)}; allowed: {', '.join(TAGS)}")
        return 1
    for kind, items in (("feature", feature_tags()), ("spell", spell_tags())):
        for item in items:
            if item["tags"] and wanted <= set(item["tags"]):
                print(f"  {kind:<8} {item['name']:<40} {', '.join(item['tags']):<28} {item['where']}")
    return 0


def write_extended(path: Path, data: dict) -> None:
    """Write an extended spell file exactly as the repo stores it: 2-space JSON, no trailing
    newline, platform line endings (git normalizes them), so a one-spell change is a one-spell diff."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_set_spell(args) -> int:
    tags = [] if args.clear else list(dict.fromkeys(args.tags))
    if not args.clear and not tags:
        print("give tags, or --clear")
        return 1
    bad = [tag for tag in tags if tag not in TAGS]
    if bad:
        print(f"unknown tag(s) {bad}; allowed: {', '.join(TAGS)}")
        return 1
    spell = next((s for s in spell_tags() if s["name"] == args.name), None)
    if spell is None:
        print(f"no spell named {args.name!r} in {', '.join(SPELL_SOURCES)} (names are case-sensitive)")
        return 1
    path = ROOT / spell["where"]
    original = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    record = {k: v for k, v in original.get(args.name, {}).items() if k != "usage_tags"}
    data = dict(original)
    # usage_tags is the first key of every existing record; keep it that way.
    data[args.name] = ({"usage_tags": tags} if tags else {}) | record
    if not data[args.name]:
        del data[args.name]
    if args.name not in original and list(original) == sorted(original):
        data = dict(sorted(data.items()))  # a sorted file stays sorted; an unsorted one gets it appended
    write_extended(path, data)
    print(f"{args.name}: {tags or 'no tags'} -> {spell['where']}")
    return 0


def cmd_spells(args) -> int:
    for spell in spell_tags():
        if args.untagged and spell["tags"]:
            continue
        if args.level is not None and spell["level"] != args.level:
            continue
        if args.cls and args.cls not in spell["classes"]:
            continue
        tags = ", ".join(spell["tags"]) if spell["tags"] else "-"
        print(f"  L{spell['level']}  {spell['name']:<36} {tags:<28} tag in {spell['where']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="validate every tag").set_defaults(run=cmd_check)
    file_parser = sub.add_parser("file", help="list each feature class in these files with its tags")
    file_parser.add_argument("paths", nargs="+")
    file_parser.set_defaults(run=cmd_file)
    with_parser = sub.add_parser("with", help="features and spells tagged with all of these tags")
    with_parser.add_argument("tags", nargs="+")
    with_parser.set_defaults(run=cmd_with)
    spells_parser = sub.add_parser("spells", help="spells as rendered, with their tags")
    spells_parser.add_argument("--untagged", action="store_true")
    spells_parser.add_argument("--level", type=int)
    spells_parser.add_argument("--class", dest="cls")
    spells_parser.set_defaults(run=cmd_spells)
    set_parser = sub.add_parser("set-spell", help="write a spell's usage_tags into the extended file that renders it")
    set_parser.add_argument("name")
    set_parser.add_argument("tags", nargs="*")
    set_parser.add_argument("--clear", action="store_true", help="remove the spell's usage_tags")
    set_parser.set_defaults(run=cmd_set_spell)
    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
