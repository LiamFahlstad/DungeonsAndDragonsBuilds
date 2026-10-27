"""Is this monster done? Every check the balance-monster workflow needs, in one call.

Usage (from the repo root):
    python .claude/skills/balance-monster/check_monster.py "Accursed"
    python .claude/skills/balance-monster/check_monster.py "Accursed" "Fresh Accursed"   # batch
    python .claude/skills/balance-monster/check_monster.py --all-homebrew               # every homebrew monster

For each monster:
  score       monster_score.py's `score`; FAIL outside 0.40-0.60
  implied CR  monster_cr_compare.py's implied CR and its distance from cr=; CHECK beyond 1 CR
  outliers    the three scored attributes furthest from the CR tier's mean (what to tune first)
  abilities   homebrew only: traits + actions + bonus actions + reactions; FAIL above 4, CHECK with no trait
  fields      homebrew only: super().__init__ keywords in the template's order; WARN on a deviation
Exit code 1 when any monster FAILs, so a clean run is the definition of "done".

The numbers come from Combat/Tools (the same code as monster_score.py and monster_cr_compare.py),
so this never disagrees with them. Use `monster_score.py -v` for the full per-attribute breakdown.
"""

import argparse
import ast
import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from Combat.Tools.generate_monster_cr_distributions import cr_key, extract_all  # noqa: E402
from Combat.Tools.monster_cr_compare import build_continuous_stats, implied_cr  # noqa: E402
from Combat.Tools.monster_score import ATTRS, build_stats, find_matches, score_monster  # noqa: E402
from Model.Creatures.Combatants import ExtendedCombatantData  # noqa: E402

BAND = (0.40, 0.60)
MAX_ABILITIES = 4
CR_TOLERANCE = 1.0
# dmg/dpr are shown by monster_score.py but never scored, so they are never "what to tune".
SCORED_LABELS = {label for _key, label, _invert, scored in ATTRS if scored}
# The order generate_monsters.py emits, plus the optional homebrew-only `description`, which every
# homebrew monster that has one places right after `combatant_type`.
OPTIONAL_FIELDS = {"description"}
FIELD_ORDER = [
    "combatant_type", "description", "hp", "ac", "temp_hp", "conditions", "ability_scores", "saving_throws",
    "spell_slots", "cr", "monster_type", "monster_type_note", "alignment", "size", "ac_note",
    "hp_formula", "speed_ground_ft", "speed_fly_ft", "speed_climb_ft", "speed_special_rules",
    "skills", "damage_vulnerabilities", "damage_resistances", "damage_immunities",
    "condition_immunities", "senses", "languages", "traits", "actions",
    "bonus_actions", "reactions", "legendary_actions", "legendary_resistances", "lair_actions",
    "mythic_actions",
]


def homebrew_classes() -> dict[str, tuple[type, Path]]:
    """combatant_type -> (class, file) for every monsters_homebrew.py class."""
    found = {}
    for path in sorted((ROOT / "Combat" / "Monsters").glob("CR_*/monsters_homebrew.py")):
        module_name = f"Combat.Monsters.{path.parent.name}.monsters_homebrew"
        module = importlib.import_module(module_name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module_name and issubclass(cls, ExtendedCombatantData):
                found[cls().combatant_type] = (cls, path)  # pyright: ignore[reportCallIssue]
    return found


def init_keywords(cls: type, path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls.__name__:
            for call in ast.walk(node):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "__init__":
                    return [k.arg for k in call.keywords if k.arg]
    return []


def field_problems(keywords: list[str]) -> list[str]:
    problems = []
    unknown = [k for k in keywords if k not in FIELD_ORDER]
    missing = [k for k in FIELD_ORDER if k not in keywords and k not in OPTIONAL_FIELDS]
    if unknown:
        problems.append("unexpected " + ", ".join(unknown))
    if missing:
        problems.append("missing " + ", ".join(missing))
    known = [k for k in keywords if k in FIELD_ORDER]
    if known != sorted(known, key=FIELD_ORDER.index):
        first = next(a for a, b in zip(known, sorted(known, key=FIELD_ORDER.index)) if a != b)
        problems.append(f"out of order from {first!r}")
    return problems


def check(m, is_homebrew, stats, attr_tiers, cr_nums, classes) -> bool:
    scores, k, breakdown = score_monster(m, stats)
    score = scores["score"]
    lines, failed = [], False

    in_band = BAND[0] <= score <= BAND[1]
    # Official monsters are reference data, not ours to rebalance: report, never fail.
    failed |= is_homebrew and not in_band
    outcome = "FAIL" if is_homebrew else "info"
    verdict = "OK" if in_band else f"{outcome} too {'strong' if score > BAND[1] else 'weak'}"
    lines.append(f"  score       {score:.2f}   {verdict} (target {BAND[0]:.2f}-{BAND[1]:.2f}, {k} scored attrs)")

    cr_val, clamped = implied_cr(m, attr_tiers, cr_nums)
    if cr_val is None:
        lines.append("  implied CR  n/a")
    else:
        delta = cr_val - cr_key(m["cr"])
        prefix = {"low": "<=", "high": ">="}.get(clamped or "", "")
        note = "OK" if abs(delta) <= CR_TOLERANCE else "CHECK cr= looks off"
        lines.append(f"  implied CR  {prefix}{cr_val:.2f}   delta {delta:+.2f}  {note}")

    scored = [(row[0], row[-1]) for row in breakdown if row[-1] is not None and row[0] in SCORED_LABELS]
    top = sorted(scored, key=lambda item: abs(item[1]), reverse=True)[:3]
    lines.append("  outliers    " + ", ".join(f"{label} {z:+.1f}" for label, z in top))

    if is_homebrew and m["name"] in classes:
        cls, path = classes[m["name"]]
        instance = cls()  # pyright: ignore[reportCallIssue]
        traits = len(instance.traits or [])
        total = traits + sum(len(getattr(instance, f) or []) for f in ("actions", "bonus_actions", "reactions"))
        if total > MAX_ABILITIES:
            failed = True
            note = f"FAIL house rule is at most {MAX_ABILITIES}"
        else:
            note = "OK" if traits else "CHECK prefer at least one trait"
        lines.append(f"  abilities   {total}/{MAX_ABILITIES}    {note} ({traits} trait{'s' if traits != 1 else ''})")
        problems = field_problems(init_keywords(cls, path))
        lines.append("  fields      " + ("OK" if not problems else "WARN " + "; ".join(problems)))
        where = f"{path.relative_to(ROOT).as_posix()}:{cls.__name__}"
    else:
        where = "official" if not is_homebrew else "homebrew (class not found)"

    print(f"{m['name']}  (CR {m['cr']}, {where})")
    print("\n".join(lines))
    result = "FAIL" if failed else ("PASS" if is_homebrew else "n/a (official monster)")
    print(f"  RESULT      {result}\n")
    return not failed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="*", help='exact combatant_type, e.g. "Accursed"')
    parser.add_argument("--all-homebrew", action="store_true", help="check every homebrew monster")
    args = parser.parse_args()
    if not args.names and not args.all_homebrew:
        parser.error("give monster names or --all-homebrew")

    data, errors = extract_all()
    for error in errors:
        print(f"warning: {error}", file=sys.stderr)
    stats = build_stats(data["monsters"])
    attr_tiers = build_continuous_stats(data["monsters"])
    cr_nums = sorted({cr_key(cr) for cr in data["cr_order"]})
    classes = homebrew_classes()

    targets, ok = [], True
    if args.all_homebrew:
        targets = [(m, True) for m in data["homebrew"]]
    for name in args.names:
        matches = find_matches(name, data["monsters"], data["homebrew"])
        if len(matches) != 1:
            listed = ", ".join(m["name"] for m, _ in matches[:8]) or "none"
            print(f'"{name}": {len(matches)} matches ({listed}); use the exact combatant_type\n')
            ok = False
            continue
        targets.append(matches[0])

    results = [check(m, hb, stats, attr_tiers, cr_nums, classes) for m, hb in targets]
    if len(results) > 1:
        print(f"{sum(results)}/{len(results)} PASS")
    return 0 if ok and all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
