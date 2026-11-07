"""Check, compare, draft and add checked spell mechanics: the entries of
CharacterContent/Spells/spells_<source>_mechanics.json that the combat UI's
Custom Effect picker fills its form from (schema: the docstring of
CharacterContent/Spells/SpellFactory/Mechanics.py).

Usage (from the repo root):
    python .claude/skills/spell-mechanics/spell_mechanics.py check
        # every entry parses, is a spell its source wins, and the files are in canonical format (exit 1 if not)
    python .claude/skills/spell-mechanics/spell_mechanics.py todo [--level N] [--class Wizard] [--campaign time_loop_pr] [--name X ...]
        # spells without an entry, and the mechanics file each belongs in
    python .claude/skills/spell-mechanics/spell_mechanics.py draft [filters as todo] --out <scratch>/draft.json
        # a draft entry per spell without one, read from its text, and a review sheet on stdout
    python .claude/skills/spell-mechanics/spell_mechanics.py add <entries.json> [--force]
        # merge reviewed entries into the right mechanics file(s), checked and formatted
    python .claude/skills/spell-mechanics/spell_mechanics.py compare [filters as todo] [--all]
        # where each checked entry and the text reading disagree (only the disagreements unless --all)
    python .claude/skills/spell-mechanics/spell_mechanics.py format
        # rewrite every mechanics file in canonical format

A draft is a starting point, never an entry: the text reading it comes from is
what these entries exist to replace. Review every field against the spell's
description before `add`.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory  # noqa: E402
from CharacterContent.Spells.SpellFactory.Mechanics import (  # noqa: E402
    parse_mechanics,
)
from Combat.CombatUIQt import effect_options as eo  # noqa: E402

# The order an entry's keys are written in.
KEY_ORDER = (
    "applicable",
    "roll",
    "save",
    "damage",
    "heal",
    "condition",
    "badge",
    "notes",
)
_LISTED_ONE_PER_LINE = ("damage", "notes")
# A monster with known numbers, so options show a DC and a bonus.
CASTER = {
    "name": "Caster",
    "actions": [
        {
            "name": "Spellcasting",
            "description": "It casts a spell (spell save DC 15, +7 to hit with spell attacks).",
        }
    ],
}
_HEAL = re.compile(
    r"regains?\s+(?:a number of\s+)?Hit Points equal to (\d+d\d+)"
    r"(\s+plus your spellcasting ability modifier)?|regains?\s+(\d+d\d+)"
)
_HEAL_UPCAST = re.compile(r"healing increases by (\d+d\d+)")


# ---------------------------------------------------------------------------
# Files


def mechanics_file(source_path: str) -> Path:
    return ROOT / SpellFactory.mechanics_path(source_path)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sources() -> dict[str, dict]:
    """Each source path, highest priority first, with its spells."""
    return {path: load_json(ROOT / path) for path in SpellFactory.json_paths}


def winning_source(name: str, all_sources: dict[str, dict]) -> str | None:
    """The source whose record SpellFactory uses for the spell."""
    return next((path for path, data in all_sources.items() if name in data), None)


def dumps(entries: dict) -> str:
    """The canonical text of a mechanics file: spells sorted, keys in
    KEY_ORDER, a damage entry or note per line, everything else inline."""
    lines = ["{"]
    names = sorted(entries)
    for index, name in enumerate(names):
        entry = entries[name]
        keys = [key for key in KEY_ORDER if key in entry]
        keys += sorted(key for key in entry if key not in KEY_ORDER)
        end = "," if index < len(names) - 1 else ""
        if not keys:
            lines.append(f"  {json.dumps(name, ensure_ascii=False)}: {{}}{end}")
            continue
        lines.append(f"  {json.dumps(name, ensure_ascii=False)}: {{")
        for key_index, key in enumerate(keys):
            value = entry[key]
            comma = "," if key_index < len(keys) - 1 else ""
            if key in _LISTED_ONE_PER_LINE and isinstance(value, list) and value:
                lines.append(f'    "{key}": [')
                for item_index, item in enumerate(value):
                    item_comma = "," if item_index < len(value) - 1 else ""
                    item_text = json.dumps(item, ensure_ascii=False)
                    lines.append(f"      {item_text}{item_comma}")
                lines.append(f"    ]{comma}")
            else:
                lines.append(
                    f'    "{key}": {json.dumps(value, ensure_ascii=False)}{comma}'
                )
        lines.append(f"  }}{end}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write(path: Path, entries: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(entries))


# ---------------------------------------------------------------------------
# Picking spells


def campaign_spells(campaign_name: str) -> set[str]:
    """The spells the campaign's party members have."""
    from Combat.PlayerCombatant import combatant_from_character
    from Combat.Scenarios import CAMPAIGNS

    campaign = CAMPAIGNS.get(campaign_name)
    if campaign is None or campaign.config is None:
        sys.exit(f"No campaign {campaign_name!r}; known: {sorted(CAMPAIGNS)}")
    names: set[str] = set()
    for builder in campaign.config.party.members:
        combatant = combatant_from_character(builder().build())
        names.update(combatant["_spell_objects"])
    return names


def chosen_spells(args) -> list:
    """The spells the filters pick, sorted by level and name."""
    wanted = set(args.name or [])
    if args.campaign:
        wanted |= campaign_spells(args.campaign)
    picked = []
    for spell in SpellFactory.all_spells():
        if wanted and spell.name not in wanted:
            continue
        if args.level is not None and spell.level != args.level:
            continue
        if args.cls and args.cls not in spell.classes:
            continue
        picked.append(spell)
    unknown = wanted - {spell.name for spell in SpellFactory.all_spells()}
    if unknown:
        sys.exit(f"Unknown spell(s): {sorted(unknown)}")
    return sorted(picked, key=lambda spell: (spell.level, spell.name))


def text_only(spell) -> DataSpell:
    """The spell without its checked mechanics: what the picker reads from
    its text."""
    data = SpellFactory._load_json()[spell.name]
    return DataSpell({key: value for key, value in data.items() if key != "mechanics"})


# ---------------------------------------------------------------------------
# Drafting


def improved_facts(spell) -> list[tuple[str, str]]:
    """Every [label, value] row of the spell's improved description, options
    included: a second reading of the same rules to check a draft against."""
    rows: list[tuple[str, str]] = []

    def walk(blocks):
        for block in blocks or []:
            if "facts" in block:
                rows.extend((label, value) for label, value in block["facts"])
            if "option" in block:
                walk(block["option"].get("blocks"))

    walk(SpellFactory._load_json()[spell.name].get("improved_description"))
    return rows


def improved_reading(spell) -> dict:
    """What the improved description's rows say the roll is."""
    facts = improved_facts(spell)
    labels = {label.lower(): value for label, value in facts}
    reading: dict = {"roll": "none", "ability": None, "dice": []}
    if "attack" in labels:
        reading["roll"] = "attack"
    elif "save" in labels:
        reading["roll"] = "save"
        word = re.match(r"\s*([A-Za-z]*)", labels["save"])[1]  # type: ignore[index]
        reading["ability"] = eo._ABILITY_SHORT_NAMES.get(word, word)
    for label in ("failed save", "on a hit", "damage"):
        if label in labels:
            reading["dice"] += re.findall(r"\d+d\d+", labels[label])
    return reading


def draft_entry(spell) -> tuple[dict, list[str]]:
    """A draft entry read from the spell's text, and what to check about it."""
    text = eo.read_effect_text(spell.description)
    entry: dict = {}
    if text.is_attack:
        entry["roll"] = "attack"
    elif text.ability is not None:
        entry["roll"] = "save"
        save: dict = {"ability": text.ability}
        if text.half_on_save:
            save["half_on_success"] = True
        if text.repeat_save:
            save["repeat"] = True
        entry["save"] = save
    else:
        entry["roll"] = "none"
    upcast = eo._upcast_dice(text.damage, text.upgrades) if spell.level else ()
    damage = []
    for index, roll in enumerate(text.damage):
        part: dict = {"dice": roll.dice, "type": roll.damage_type}
        if roll.damage_type is None:
            part["choices"] = []
        if text.adds_modifier:
            part["add_modifier"] = True
        if upcast and upcast[index]:
            part["upcast"] = upcast[index]
        damage.append(part)
    if spell.level == 0 and len(damage) == 1:
        steps = dict(
            (at, dice)
            for upgrade in text.upgrades
            for at, dice in eo._CANTRIP_STEP.findall(upgrade)
        )
        if set(steps) == {"5", "11", "17"}:
            damage[0]["cantrip"] = steps
    if damage:
        entry["damage"] = damage
    heal = _HEAL.search(spell.description)
    if heal is not None:
        entry["heal"] = {"dice": heal[1] or heal[3]}
        if heal[2]:
            entry["heal"]["add_modifier"] = True
        more = _HEAL_UPCAST.search(spell.description)
        if more is not None:
            entry["heal"]["upcast"] = more[1]
    if text.condition:
        condition: dict = {"name": text.condition}
        if text.until:
            condition["until"] = list(text.until)
        entry["condition"] = condition
    checks = list(text.notes)
    improved = improved_reading(spell)
    if improved_facts(spell):
        mismatches = []
        if improved["roll"] != entry["roll"]:
            mismatches.append(f"roll: improved says {improved['roll']}")
        ability = entry.get("save", {}).get("ability")
        if improved["ability"] and improved["ability"] != ability:
            mismatches.append(f"save: improved says {improved['ability']}")
        dice = [part["dice"].split()[0] for part in damage]
        if improved["dice"] and dice and improved["dice"][: len(dice)] != dice:
            mismatches.append(f"damage: improved says {improved['dice']}")
        checks.append(
            "Improved description DIFFERS: " + "; ".join(mismatches)
            if mismatches
            else "Improved description agrees on roll, save and damage."
        )
    else:
        checks.append("No improved description to check against.")
    return entry, checks


# ---------------------------------------------------------------------------
# Commands


def cmd_check(_args) -> int:
    problems = []
    all_sources = sources()
    for source_path, source in all_sources.items():
        path = mechanics_file(source_path)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        entries = json.loads(text)
        rel = path.relative_to(ROOT).as_posix()
        for name, value in entries.items():
            if name not in source:
                problems.append(f"{rel}: {name!r} isn't a spell of {source_path}")
                continue
            if winning_source(name, all_sources) != source_path:
                winner = winning_source(name, all_sources)
                problems.append(
                    f"{rel}: {name!r} is never used: {winner} wins for that spell"
                )
            try:
                parse_mechanics(name, value)
            except ValueError as error:
                problems.append(f"{rel}: {error}")
        if text != dumps(entries):
            problems.append(f"{rel}: not in canonical format (run `format`)")
        print(f"{rel}: {len(entries)} entries")
    for problem in problems:
        print("PROBLEM", problem)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_todo(args) -> int:
    all_sources = sources()
    missing = [spell for spell in chosen_spells(args) if spell.mechanics is None]
    for spell in missing:
        source = winning_source(spell.name, all_sources) or "?"
        target = SpellFactory.mechanics_path(source).split("/")[-1]
        print(f"L{spell.level} {spell.name:32} -> {target}")
    print(f"{len(missing)} spell(s) without an entry")
    return 0


def cmd_draft(args) -> int:
    drafts = {}
    for spell in chosen_spells(args):
        if spell.mechanics is not None:
            continue
        entry, checks = draft_entry(spell)
        drafts[spell.name] = entry
        print(f"===== {spell.name} (level {spell.level}, {spell.source})")
        print(f"Casting time: {spell.casting_time} | Duration: {spell.duration}")
        print(spell.description)
        print("Draft:", json.dumps(entry, ensure_ascii=False))
        for check in checks:
            print("Check:", check)
        print()
    if args.out:
        Path(args.out).write_text(dumps(drafts), encoding="utf-8")
        print(f"{len(drafts)} draft(s) written to {args.out}")
    return 0


def cmd_add(args) -> int:
    with open(args.file, encoding="utf-8") as f:
        new = json.load(f)
    all_sources = sources()
    by_file: dict[Path, dict] = {}
    problems = []
    for name, value in new.items():
        source_path = winning_source(name, all_sources)
        if source_path is None:
            problems.append(f"{name!r} is not a spell")
            continue
        try:
            parse_mechanics(name, value)
        except ValueError as error:
            problems.append(str(error))
            continue
        path = mechanics_file(source_path)
        entries = by_file.setdefault(path, load_json(path))
        if name in entries and not args.force and entries[name] != value:
            problems.append(f"{name!r} already has an entry (use --force)")
            continue
        entries[name] = value
    if problems:
        for problem in problems:
            print("PROBLEM", problem)
        print("Nothing written.")
        return 1
    for path, entries in by_file.items():
        write(path, entries)
        print(f"{path.relative_to(ROOT).as_posix()}: {len(entries)} entries")
    return 0


_COMPARED = (
    ("roll", lambda o: o.roll),
    ("ability", lambda o: o.ability),
    ("half", lambda o: o.half_on_save),
    ("repeat", lambda o: o.repeat_save),
    ("damage", lambda o: o.damage),
    ("upcast", lambda o: o.upcast),
    ("condition", lambda o: o.condition),
    ("until", lambda o: o.until),
)


def cmd_compare(args) -> int:
    for spell in chosen_spells(args):
        if spell.mechanics is None:
            continue
        curated = eo.spell_option(spell, CASTER)
        read = eo.spell_option(text_only(spell), CASTER)
        differences = [
            f"{label}: checked {get(curated)!r}, text {get(read)!r}"
            for label, get in _COMPARED
            if get(curated) != get(read)
        ]
        if differences or args.all:
            print(f"{spell.name}: {'same' if not differences else ''}")
            for difference in differences:
                print("   ", difference)
    return 0


def cmd_format(_args) -> int:
    for source_path in SpellFactory.json_paths:
        path = mechanics_file(source_path)
        if path.exists():
            write(path, load_json(path))
            print(f"formatted {path.relative_to(ROOT).as_posix()}")
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    commands.add_parser("format")
    for name in ("todo", "draft", "compare"):
        command = commands.add_parser(name)
        command.add_argument("--level", type=int)
        command.add_argument("--class", dest="cls")
        command.add_argument("--campaign")
        command.add_argument("--name", action="append", help="repeatable")
        if name == "draft":
            command.add_argument("--out", help="write the drafts here (scratch dir)")
        if name == "compare":
            command.add_argument("--all", action="store_true")
    add = commands.add_parser("add")
    add.add_argument("file")
    add.add_argument("--force", action="store_true")
    args = parser.parse_args()
    handler = {
        "check": cmd_check,
        "todo": cmd_todo,
        "draft": cmd_draft,
        "add": cmd_add,
        "compare": cmd_compare,
        "format": cmd_format,
    }[args.command]
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
