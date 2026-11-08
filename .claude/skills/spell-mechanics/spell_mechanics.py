"""Check, compare, draft and add spells' combat effects: the entries of
CharacterContent/Spells/spells_<source>_combat_effects.json that the combat
UI's Custom Effect picker fills its form from. A spell written as a class
(CharacterContent/Spells/SpellClasses) has its combat effects in its class
instead: `todo` counts it as described, and `add` refuses it. An entry is a list of
CombatEffect dicts (Model/Content/CombatEffect.py: what to_dict() writes and
from_dict() reads), one per way to cast the spell, or [] for a spell with
nothing to apply.

Usage (from the repo root):
    python .claude/skills/spell-mechanics/spell_mechanics.py check
        # every entry reads, is a spell its source wins, follows the rubric's checks, and the files are canonical (exit 1 if not)
    python .claude/skills/spell-mechanics/spell_mechanics.py todo [--level N] [--class Wizard] [--campaign time_loop_pr] [--name X ...]
        # spells without an entry, and the file each belongs in
    python .claude/skills/spell-mechanics/spell_mechanics.py draft [filters as todo] --out <scratch>/draft.json
        # a draft entry per spell without one, read from its text, and a review sheet on stdout
    python .claude/skills/spell-mechanics/spell_mechanics.py add <entries.json> [--force]
        # merge reviewed entries into the right file(s), checked and formatted
    python .claude/skills/spell-mechanics/spell_mechanics.py compare [filters as todo] [--all]
        # where each checked entry and the text reading disagree (only the disagreements unless --all)
    python .claude/skills/spell-mechanics/spell_mechanics.py format
        # rewrite every combat effects file in canonical format

A draft is a starting point, never an entry: the text reading it comes from is
what these entries exist to replace. Review every field against the spell's
description before `add`.
"""

import argparse
import json
import re
import sys
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory  # noqa: E402
from Combat.CombatUIQt import effect_options as eo  # noqa: E402
from Core.Definitions import Ability, Condition  # noqa: E402
from Model.Content.CombatEffect import CombatEffect  # noqa: E402

# The order an effect's keys are written in: CombatEffect's own.
KEY_ORDER = tuple(field.name for field in fields(CombatEffect))
_LISTED_ONE_PER_LINE = ("damage", "notes")
_CONDITIONS = {condition.value for condition in Condition}
_SHORT_ABILITY = {ability.short_name: ability.value for ability in Ability}
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


# ---------------------------------------------------------------------------
# Files


def effects_file(source_path: str) -> Path:
    return ROOT / SpellFactory.combat_effects_path(source_path)


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


def _dump_effect(effect: dict, indent: str) -> list[str]:
    """One effect's lines: keys in KEY_ORDER, a damage part or note per line,
    everything else inline."""
    keys = [key for key in KEY_ORDER if key in effect]
    keys += sorted(key for key in effect if key not in KEY_ORDER)
    lines = [f"{indent}{{"]
    for index, key in enumerate(keys):
        value = effect[key]
        comma = "," if index < len(keys) - 1 else ""
        if key in _LISTED_ONE_PER_LINE and isinstance(value, list) and value:
            lines.append(f'{indent}  "{key}": [')
            for item_index, item in enumerate(value):
                item_comma = "," if item_index < len(value) - 1 else ""
                item_text = json.dumps(item, ensure_ascii=False)
                lines.append(f"{indent}    {item_text}{item_comma}")
            lines.append(f"{indent}  ]{comma}")
        else:
            text = json.dumps(value, ensure_ascii=False)
            lines.append(f'{indent}  "{key}": {text}{comma}')
    lines.append(f"{indent}}}")
    return lines


def dumps(entries: dict) -> str:
    """The canonical text of a combat effects file: spells sorted, each a
    list of effects (see _dump_effect)."""
    lines = ["{"]
    names = sorted(entries)
    for index, name in enumerate(names):
        effects = entries[name]
        end = "," if index < len(names) - 1 else ""
        key = json.dumps(name, ensure_ascii=False)
        if not isinstance(effects, list) or not effects:
            lines.append(f"  {key}: {json.dumps(effects, ensure_ascii=False)}{end}")
            continue
        lines.append(f"  {key}: [")
        for effect_index, effect in enumerate(effects):
            effect_lines = _dump_effect(effect, "    ")
            if effect_index < len(effects) - 1:
                effect_lines[-1] += ","
            lines.extend(effect_lines)
        lines.append(f"  ]{end}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def normalized(entries: dict) -> dict:
    """The entries with each effect that reads rewritten as to_dict() writes
    it (its keys in their canonical order); one that doesn't read is kept
    as it is, for `check` to report."""
    result = {}
    for name, value in entries.items():
        if not isinstance(value, list):
            result[name] = value
            continue
        effects = []
        for data in value:
            try:
                effects.append(CombatEffect.from_dict(data).to_dict())
            except ValueError:
                effects.append(data)
        result[name] = effects
    return result


def write(path: Path, entries: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(normalized(entries)))


def entry_problems(name: str, value, spell) -> list[str]:
    """What's wrong with a spell's entry: it doesn't read, it isn't written
    as to_dict() would write it, or it breaks a rubric rule a script can
    check (a condition that's neither a rules condition nor the spell's own
    badge, cantrip dice on a levelled spell)."""
    if not isinstance(value, list):
        return [f"{name!r}: expected a list of effects, got {value!r}"]
    problems = []
    for index, data in enumerate(value):
        try:
            effect = CombatEffect.from_dict(data, f"spell {name!r}[{index}]")
        except ValueError as error:
            problems.append(str(error))
            continue
        if effect.to_dict() != data:
            problems.append(
                f"{name!r}[{index}]: not as to_dict() writes it (a default"
                f" value written out?): {json.dumps(effect.to_dict())}"
            )
        for condition in effect.conditions:
            if condition.name not in _CONDITIONS | {name}:
                problems.append(
                    f"{name!r}[{index}]: condition {condition.name!r} is neither"
                    " a rules condition nor the spell's own name (its badge)"
                )
        if (
            spell is not None
            and spell.level > 0
            and any(d.cantrip for d in effect.damage)
        ):
            problems.append(
                f"{name!r}[{index}]: cantrip steps on a level {spell.level} spell"
            )
        if (
            spell is not None
            and spell.level == 0
            and any(d.upcast for d in effect.damage)
        ):
            problems.append(f"{name!r}[{index}]: upcast on a cantrip")
    return problems


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
    # A name or campaign filter that finds no spells (a campaign without a
    # party yet) picks none, not every spell.
    by_name = bool(args.name or args.campaign)
    picked = []
    for spell in SpellFactory.all_spells():
        if by_name and spell.name not in wanted:
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
    """The spell without its checked combat effects: what the picker reads
    from its text."""
    data = SpellFactory._load_json()[spell.name]
    return DataSpell(
        {key: value for key, value in data.items() if key != "combat_effects"}
    )


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
    reading: dict = {"roll": "none", "save_ability": None, "dice": []}
    if "attack" in labels:
        reading["roll"] = "attack"
    elif "save" in labels:
        reading["roll"] = "save"
        word = re.match(r"\s*([A-Za-z]*)", labels["save"])[1]  # type: ignore[index]
        reading["save_ability"] = _SHORT_ABILITY.get(word, word)
    for label in ("failed save", "on a hit", "damage"):
        if label in labels:
            reading["dice"] += re.findall(r"\d+d\d+", labels[label])
    return reading


def draft_entry(spell) -> tuple[list, list[str]]:
    """A draft entry (one effect) read from the spell's text, and what to
    check about it."""
    text = eo.read_effect_text(spell.description)
    effect: dict = {}
    if text.is_attack:
        effect["roll"] = "attack"
    elif text.ability is not None:
        effect["roll"] = "save"
        effect["save_ability"] = _SHORT_ABILITY[text.ability]
        if text.half_on_save:
            effect["half_on_success"] = True
        if text.repeat_save:
            effect["repeat_save"] = True
    upcast = eo._upcast_dice(text.damage, text.upgrades) if spell.level else ()
    damage = []
    for index, roll in enumerate(text.damage):
        part: dict = {"dice": roll.dice, "damage_type": roll.damage_type}
        if roll.damage_type is None:
            part["choices"] = []
        if upcast and upcast[index]:
            part["upcast"] = upcast[index]
        if text.adds_modifier:
            part["add_modifier"] = True
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
        effect["damage"] = damage
    gain = text.gain  # the combat UI's own reading of healing
    if gain is not None and not damage:
        key = "temp_hp" if gain.temporary else "healing"
        effect[key] = {"dice": gain.dice}
        if gain.upcast:
            effect[key]["upcast"] = gain.upcast
        if gain.add_modifier:
            effect[key]["add_modifier"] = True
    if text.condition:
        condition: dict = {"name": text.condition}
        if text.until:
            condition["until"] = list(text.until)
        effect["conditions"] = [condition]
    elif not (damage or gain or spell.duration_seconds == 0):
        # What the picker did before entries said so: a spell with nothing
        # else to show puts its own name on its targets. Keep it or drop it.
        effect["conditions"] = [{"name": spell.name}]
    checks = list(text.notes)
    if gain is not None and damage:
        checks.append("It also gives Hit Points: say so in notes.")
    if effect.get("conditions") == [{"name": spell.name}]:
        checks.append("Its own name as a badge: keep it only if it marks the target.")
    improved = improved_reading(spell)
    if improved_facts(spell):
        mismatches = []
        if improved["roll"] != effect.get("roll", "none"):
            mismatches.append(f"roll: improved says {improved['roll']}")
        ability = effect.get("save_ability")
        if improved["save_ability"] and improved["save_ability"] != ability:
            mismatches.append(f"save: improved says {improved['save_ability']}")
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
    return [effect], checks


# ---------------------------------------------------------------------------
# Commands


def cmd_check(_args) -> int:
    problems = []
    all_sources = sources()
    for source_path, source in all_sources.items():
        path = effects_file(source_path)
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
            if name in SpellFactory._spell_classes():
                problems.append(
                    f"{rel}: {name!r} is never used: the spell has a class"
                    " (CharacterContent/Spells/SpellClasses); edit its class"
                )
            spell = DataSpell(source[name])
            problems += [f"{rel}: {p}" for p in entry_problems(name, value, spell)]
        if text != dumps(normalized(entries)):
            problems.append(f"{rel}: not in canonical format (run `format`)")
        print(f"{rel}: {len(entries)} entries")
    for problem in problems:
        print("PROBLEM", problem)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_todo(args) -> int:
    all_sources = sources()
    missing = [s for s in chosen_spells(args) if s.combat_effects() is None]
    for spell in missing:
        source = winning_source(spell.name, all_sources) or "?"
        target = SpellFactory.combat_effects_path(source).split("/")[-1]
        print(f"L{spell.level} {spell.name:32} -> {target}")
    print(f"{len(missing)} spell(s) without an entry")
    return 0


def cmd_draft(args) -> int:
    drafts = {}
    for spell in chosen_spells(args):
        if spell.combat_effects() is not None:
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
        if name in SpellFactory._spell_classes():
            module = SpellFactory._spell_classes()[name].__module__
            problems.append(
                f"{name!r} has a class ({module}): write its combat_effects()"
                " there, not in a JSON entry"
            )
            continue
        spell = DataSpell(all_sources[source_path][name])
        found = entry_problems(name, value, spell)
        if found:
            problems += found
            continue
        path = effects_file(source_path)
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
        if spell.combat_effects() is None:
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
        path = effects_file(source_path)
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
