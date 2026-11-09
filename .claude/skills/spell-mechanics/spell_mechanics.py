"""Check, compare, draft and add spells' combat effects: what a spell's
combat_effects() returns, which the combat UI's Custom Effect picker fills
its form from. They are written in Python, in the spell's class
(CharacterContent/Spells/SpellClasses): a list of CombatEffect objects
(Model/Content/CombatEffect.py), one per way to cast the spell, or [] for a
spell with nothing to apply. Every spell is a class; `add` turns a spell
scraped since (a JSON record without a class) into one to give it its
effects (CharacterContent/Spells/SpellClassConverter.py).

Usage (from the repo root):
    python .claude/skills/spell-mechanics/spell_mechanics.py check
        # every class's effects follow the rubric's checks (exit 1 if not)
    python .claude/skills/spell-mechanics/spell_mechanics.py todo [--level N] [--class Wizard] [--campaign time_loop_pr] [--name X ...]
        # spells without combat effects, and where each one's go
    python .claude/skills/spell-mechanics/spell_mechanics.py draft [filters as todo] --out <scratch>/draft.py
        # a draft per spell without effects, read from its text, as Python, and a review sheet on stdout
    python .claude/skills/spell-mechanics/spell_mechanics.py add <scratch>/draft.py [--force]
        # check the reviewed EFFECTS and write each into its spell's class (made from its JSON if need be)
    python .claude/skills/spell-mechanics/spell_mechanics.py compare [filters as todo] [--all]
        # where each spell's effects and the text reading disagree (only the disagreements unless --all)

A draft is a starting point, never an entry: the text reading it comes from is
what these effects exist to replace. Review every field against the spell's
description before `add`.
"""

import argparse
import re
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from CharacterContent.Spells import SpellClassConverter as converter  # noqa: E402
from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory  # noqa: E402
from Combat.CombatUIQt import effect_options as eo  # noqa: E402
from Core.Definitions import Ability, Condition  # noqa: E402
from Model.Content.CombatEffect import CombatEffect  # noqa: E402
from Model.Content.FeatureText import Facts, Option  # noqa: E402

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
# The rubric's checks


def effect_problems(name: str, effects: list[CombatEffect], spell) -> list[str]:
    """Where a spell's effects break a rubric rule a script can check: a
    condition that's neither a rules condition nor the spell's own badge,
    cantrip dice on a levelled spell, upcast dice on a cantrip."""
    problems = []
    for index, effect in enumerate(effects):
        for condition in effect.conditions:
            if condition.name not in _CONDITIONS | {name}:
                problems.append(
                    f"{name!r}[{index}]: condition {condition.name!r} is neither"
                    " a rules condition nor the spell's own name (its badge)"
                )
        if spell.level > 0 and any(d.cantrip for d in effect.damage):
            problems.append(
                f"{name!r}[{index}]: cantrip steps on a level {spell.level} spell"
            )
        if spell.level == 0 and any(d.upcast for d in effect.damage):
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


def text_only(spell) -> DataSpell | None:
    """The spell as its scraped record, which has no combat effects: what
    the picker reads from its text. None for a spell only a class has."""
    data = SpellFactory._load_json().get(spell.name)
    if data is None:
        return None
    return DataSpell(data)


def destination(spell) -> str:
    """Where `add` writes the spell's effects."""
    classes = SpellFactory._spell_classes()
    if spell.name in classes:
        module = classes[spell.name].__module__.rsplit(".", 1)[-1]
        return f"class in {module}.py"
    try:
        converter.class_source(spell)
    except converter.CannotConvert as reason:
        return f"nowhere yet: can't be a class ({reason}); fix its record first"
    return f"new class in {converter.module_name(spell.level)}.py"


# ---------------------------------------------------------------------------
# Drafting


def improved_facts(spell) -> list[tuple[str, str]]:
    """Every [label, value] row of the spell's improved description, options
    included: a second reading of the same rules to check a draft against."""
    rows: list[tuple[str, str]] = []

    def walk(blocks):
        for block in blocks or ():
            if isinstance(block, Facts):
                rows.extend((label, value) for label, value in block.rows)
            elif isinstance(block, Option):
                walk(block.blocks)

    walk(spell.improved_description)
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
    # Every row with one of these labels, in order: a spell often has two
    # "Damage" rows, what it deals and, later, "+1d6 for each slot level".
    for wanted in ("failed save", "on a hit", "damage"):
        for label, value in facts:
            if label.lower() == wanted and not value.lstrip().startswith("+"):
                reading["dice"] += re.findall(r"\d+d\d+", value)
    return reading


def draft_entry(spell) -> tuple[list, list[str]]:
    """A draft entry (one effect, as to_dict() data) read from the spell's
    text, and what to check about it."""
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


def draft_source(entry: list) -> tuple[str, str | None]:
    """A draft entry as Python: CombatEffect calls with enums, as the
    spell's class will say it. One the model refuses (a damage type to
    choose with no choices yet) stays a dict, with the reason, so `add`
    refuses it until it's written out."""
    try:
        effects = [CombatEffect.from_dict(data) for data in entry]
    except ValueError as error:
        return repr(entry), str(error)
    return converter.source_of(effects), None


_DRAFT_HEAD = '''"""Combat effects drafted from each spell's text by spell_mechanics.py
draft: a starting point, never an entry. Review every effect against the
spell's full description (the review sheet) and the skill's rubric, then
    python .claude/skills/spell-mechanics/spell_mechanics.py add <this file>
which writes each spell's list into its class's combat_effects().
"""
'''


def draft_module(drafts: dict[str, tuple[str, list[str]]]) -> str:
    """The draft file: EFFECTS, each spell's draft as Python with its checks
    as comments above it, and the imports that needs."""
    body = ["EFFECTS = {"]
    for name, (source, checks) in drafts.items():
        body += [f"    # {line}" for check in checks for line in check.splitlines()]
        body.append(f"    {name!r}: {source},")
    body.append("}")
    code = "\n".join(body) + "\n"
    names = converter._names_used(code)
    by_module: dict[str, set[str]] = {}
    for name in names:
        by_module.setdefault(converter._IMPORTS[name], set()).add(name)
    imports = [
        f"from {module} import {', '.join(sorted(items))}"
        for module, items in sorted(by_module.items())
    ]
    return _DRAFT_HEAD + "\n" + "\n".join(imports) + "\n\n" + code


def load_effects(path: str) -> dict:
    """The EFFECTS a reviewed draft file defines."""
    namespace = runpy.run_path(path)
    effects = namespace.get("EFFECTS")
    if not isinstance(effects, dict):
        sys.exit(f"{path} defines no EFFECTS dict")
    return effects


# ---------------------------------------------------------------------------
# Commands


def cmd_check(_args) -> int:
    problems = []
    classes = SpellFactory._spell_classes()
    described = 0
    for name, spell_class in sorted(classes.items()):
        where = spell_class.__module__.rsplit(".", 1)[-1] + ".py"
        try:
            spell = spell_class()
            effects = spell.combat_effects()
        except Exception as error:  # a class whose effects don't build
            problems.append(f"{where}: {name!r}: {error!r}")
            continue
        if effects is None:
            continue
        described += 1
        problems += [f"{where}: {p}" for p in effect_problems(name, effects, spell)]
    print(f"spell classes: {described} of {len(classes)} with combat effects")
    for problem in problems:
        print("PROBLEM", problem)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_todo(args) -> int:
    missing = [s for s in chosen_spells(args) if s.combat_effects() is None]
    for spell in missing:
        print(f"L{spell.level} {spell.name:32} -> {destination(spell)}")
    print(f"{len(missing)} spell(s) without combat effects")
    return 0


def cmd_draft(args) -> int:
    drafts: dict[str, tuple[str, list[str]]] = {}
    for spell in chosen_spells(args):
        if spell.combat_effects() is not None:
            continue
        entry, checks = draft_entry(spell)
        source, refused = draft_source(entry)
        if refused:
            checks.append(
                f"NOT AN EFFECT YET ({refused}): write it as CombatEffect(...)"
            )
        checks.insert(0, f"{spell.name}: level {spell.level}, -> {destination(spell)}")
        drafts[spell.name] = (source, checks)
        print(f"===== {spell.name} (level {spell.level}, {spell.source})")
        print(f"Casting time: {spell.casting_time} | Duration: {spell.duration}")
        print(spell.description)
        print("Draft:", source)
        for check in checks[1:]:
            print("Check:", check)
        print()
    if args.out:
        Path(args.out).write_text(draft_module(drafts), encoding="utf-8")
        subprocess.run([sys.executable, "-m", "black", "-q", args.out], check=False)
        print(f"{len(drafts)} draft(s) written to {args.out}")
    return 0


def cmd_add(args) -> int:
    new = load_effects(args.file)
    records = SpellFactory._load_json()
    classes = SpellFactory._spell_classes()
    to_set: dict[str, list[CombatEffect]] = {}
    to_convert: dict[str, list[CombatEffect]] = {}
    unchanged = []
    problems = []
    for name, value in new.items():
        if name not in classes and name not in records:
            problems.append(f"{name!r} is not a spell")
            continue
        if not isinstance(value, list) or not all(
            isinstance(effect, CombatEffect) for effect in value
        ):
            problems.append(
                f"{name!r}: expected a list of CombatEffect, got {value!r}"
                " (a draft that didn't build? write it as CombatEffect(...))"
            )
            continue
        spell = SpellFactory.create(name)
        found = effect_problems(name, value, spell)
        if found:
            problems += found
            continue
        old = spell.combat_effects()
        if old == value:
            unchanged.append(name)
            continue
        if old is not None and not args.force:
            problems.append(f"{name!r} already has combat effects (use --force)")
            continue
        if name in classes:
            to_set[name] = value
            continue
        try:
            converter.class_source(DataSpell(records[name]), value)
        except converter.CannotConvert as reason:
            problems.append(
                f"{name!r} can't be a class ({reason}): fix its record first"
            )
            continue
        to_convert[name] = value
    if problems:
        for problem in problems:
            print("PROBLEM", problem)
        print("Nothing written.")
        return 1

    status = 0
    if to_convert:
        result = converter.convert(
            [DataSpell(records[name]) for name in to_convert], to_convert
        )
        status |= _report(result, "converted to a class, with these effects")
    if to_set:
        result = converter.set_combat_effects(to_set)
        status |= _report(result, "combat_effects() written in its class")
    for name in unchanged:
        print(f"{name}: unchanged")
    return status


def _report(result, what: str) -> int:
    if result.problems:
        for problem in result.problems:
            print("PROBLEM", problem)
        print("Nothing kept of that step: its files were put back.")
        return 1
    for name in result.done:
        print(f"{name}: {what}")
    for path in result.written:
        print(f"  wrote {path.relative_to(ROOT).as_posix()}")
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
        record = text_only(spell)
        if record is None:
            print(f"{spell.name}: no scraped record, no text reading to compare")
            continue
        curated = eo.spell_option(spell, CASTER)
        read = eo.spell_option(record, CASTER)
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


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
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
    add.add_argument("file", help="a reviewed draft: a .py file defining EFFECTS")
    add.add_argument("--force", action="store_true")
    args = parser.parse_args()
    handler = {
        "check": cmd_check,
        "todo": cmd_todo,
        "draft": cmd_draft,
        "add": cmd_add,
        "compare": cmd_compare,
    }[args.command]
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
