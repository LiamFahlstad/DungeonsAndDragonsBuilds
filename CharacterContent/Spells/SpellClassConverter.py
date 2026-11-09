"""Turn spells' JSON into classes (CharacterContent/Spells/SpellFactory/
ClassSpell.py): one class per spell, written into the module of its level in
CharacterContent/Spells/SpellClasses/ (Cantrips.py, Level1.py, ...), from
everything the JSON says about it - the winning source's record (the
rules), and its companions: usage_tags and target (_extended), the improved
description (_improved) and the combat effects (_combat_effects).

The class then is the spell's one source: SpellFactory uses it instead of
the JSON, and the converter takes the spell's entries out of the companion
files so the two can't drift apart. The scraped source record stays, as the
fallback the class replaces and what a re-scrape is compared against.

Usage (from the repo root):
    python -m CharacterContent.Spells.SpellClassConverter --name Fireball --name "Magic Missile"
    python -m CharacterContent.Spells.SpellClassConverter --described   # every spell with combat effects
    python -m CharacterContent.Spells.SpellClassConverter --level 3     # every level 3 spell
    python -m CharacterContent.Spells.SpellClassConverter --all
    ... --dry-run     # print the classes, write nothing
    ... --keep-json   # write the classes, leave the companion files as they are

A spell that already has a class is skipped: the class may have been edited
by hand since. Each class is checked before anything is written to the
companion files: built by the factory, it must give the same rules, tags,
target, improved description and combat effects as the JSON did. The casting
time, range, components and duration are compared as what they mean
(SpellFields), not as text: the class writes them in the 2024 wording.
"""

import argparse
import ast
import dataclasses
import enum
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory  # noqa: E402
from CharacterContent.Spells.SpellFactory.ClassSpell import SpellRules  # noqa: E402
from CharacterContent.Spells.SpellFactory.Enums import School  # noqa: E402
from CharacterContent.Spells.SpellFactory.SpellFields import (  # noqa: E402
    CastingTime,
    Components,
    Duration,
    Range,
)
from Core.Definitions import CharacterClass, Condition  # noqa: E402

CLASSES_DIR = ROOT / "CharacterContent" / "Spells" / "SpellClasses"
PACKAGE = "CharacterContent.Spells.SpellClasses"

# What the generated code can name, and where each comes from.
_IMPORTS = {
    "Ability": "Core.Definitions",
    "CharacterClass": "Core.Definitions",
    "Condition": "Core.Definitions",
    "DamageType": "Core.Definitions",
    "AreaShape": "CharacterContent.Spells.SpellFactory.Enums",
    "CastingTimeType": "CharacterContent.Spells.SpellFactory.Enums",
    "DurationType": "CharacterContent.Spells.SpellFactory.Enums",
    "RangeType": "CharacterContent.Spells.SpellFactory.Enums",
    "School": "CharacterContent.Spells.SpellFactory.Enums",
    "Area": "CharacterContent.Spells.SpellFactory.SpellFields",
    "CastingTime": "CharacterContent.Spells.SpellFactory.SpellFields",
    "Components": "CharacterContent.Spells.SpellFactory.SpellFields",
    "Duration": "CharacterContent.Spells.SpellFactory.SpellFields",
    "Range": "CharacterContent.Spells.SpellFactory.SpellFields",
    "ActionType": "Model.Content.ActionType",
    "CombatCondition": "Model.Content.CombatEffect",
    "CombatDamage": "Model.Content.CombatEffect",
    "CombatEffect": "Model.Content.CombatEffect",
    "CombatHitPoints": "Model.Content.CombatEffect",
    "CombatInstances": "Model.Content.CombatEffect",
    "FeatureTarget": "Model.Content.Feature",
    "Block": "Model.Content.FeatureText",
    "Facts": "Model.Content.FeatureText",
    "LevelTrack": "Model.Content.FeatureText",
    "Option": "Model.Content.FeatureText",
    "Paragraph": "Model.Content.FeatureText",
    "Table": "Model.Content.FeatureText",
    "CharacterView": "Model.View",
    "ClassSpell": "CharacterContent.Spells.SpellFactory.ClassSpell",
    "SpellRules": "CharacterContent.Spells.SpellFactory.ClassSpell",
}
# Fields written positionally even though they have a default, as the
# hand-written code does: Option("Name", (blocks)), CombatDamage(dice, type,
# choices), Range(RangeType.FOOT, 60), Duration(DurationType.MINUTE, 1).
_POSITIONAL = {
    ("Option", "blocks"),
    ("CombatDamage", "choices"),
    ("CastingTime", "amount"),
    ("Range", "amount"),
    ("Duration", "amount"),
}
# Written all by keyword: ten strings in a row say nothing by position.
_BY_KEYWORD = {"SpellRules"}
# Text a model keeps as text but that names an enum member, written as the
# member: CombatCondition("Prone") is CombatCondition(Condition.PRONE). A
# badge's name ("Bless") stays text.
_AS_ENUM = {("CombatCondition", "name"): Condition}


class CannotConvert(ValueError):
    """A spell whose JSON says something the class's enums and dataclasses
    can't: a class or school with a note ("Wizard (Dunamancy)"), a casting
    time SpellFields can't read, no components at all. It stays JSON until
    it's converted by hand."""


# Record keys the rules don't need: the 2014 source's "ritual" is in its
# casting time too.
_IGNORED_KEYS = {"ritual"}
_RULE_KEYS = {
    "name",
    "level",
    "school",
    "classes",
    "casting_time",
    "range",
    "components",
    "duration",
    "description",
    "source",
}
_COMPANION_KEYS = {"usage_tags", "target", "improved_description", "combat_effects"}


# ---------------------------------------------------------------------------
# Python source for values


def source_of(value) -> str:
    """`value` as Python source: dataclasses as constructor calls (required
    fields positional, the rest by keyword and only when not the default),
    enums by name, tuples and lists as such."""
    if isinstance(value, enum.Enum):
        return f"{type(value).__name__}.{value.name}"
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        name = type(value).__name__
        args = []
        for field in dataclasses.fields(value):
            item = getattr(value, field.name)
            enum_type = _AS_ENUM.get((name, field.name))
            if enum_type is not None and item in {m.value for m in enum_type}:
                item = enum_type(item)
            has_default = (
                field.default is not dataclasses.MISSING
                or field.default_factory is not dataclasses.MISSING
            )
            default = (
                field.default
                if field.default is not dataclasses.MISSING
                else (
                    field.default_factory()
                    if field.default_factory is not dataclasses.MISSING
                    else None
                )
            )
            if name in _BY_KEYWORD:
                if not has_default or item != default:
                    args.append(f"{field.name}={source_of(item)}")
            elif not has_default or (name, field.name) in _POSITIONAL:
                if (
                    has_default
                    and item == default
                    and (name, field.name) in _POSITIONAL
                ):
                    continue
                args.append(source_of(item))
            elif item != default:
                args.append(f"{field.name}={source_of(item)}")
        return f"{name}({', '.join(args)})"
    if isinstance(value, tuple):
        if len(value) == 1:
            return f"({source_of(value[0])},)"
        return f"({', '.join(source_of(item) for item in value)})"
    if isinstance(value, list):
        return f"[{', '.join(source_of(item) for item in value)}]"
    if isinstance(value, str) and "\n" in value:
        lines = value.split("\n")
        parts = [repr(line + "\n") for line in lines[:-1]] + [repr(lines[-1])]
        return "(" + " ".join(part for part in parts if part != "''") + ")"
    return repr(value)


def class_name(spell_name: str) -> str:
    """ "Tasha's Hideous Laughter" -> "TashasHideousLaughter"."""
    words = re.findall(r"[A-Za-z0-9]+", spell_name.replace("'", "").replace("’", ""))
    name = "".join(word[:1].upper() + word[1:] for word in words)
    if not name or name[0].isdigit():
        name = f"Spell{name}"
    return name


def module_name(level: int) -> str:
    return "Cantrips" if level == 0 else f"Level{level}"


def class_source(spell: DataSpell) -> str:
    """The class for `spell`, a JSON spell with its companions merged."""
    data = spell._data
    unknown = set(data) - _RULE_KEYS - _COMPANION_KEYS - _IGNORED_KEYS
    if unknown:
        raise ValueError(
            f"{spell.name}: record keys the converter can't keep: {unknown}"
        )
    if not spell._data.get("components"):
        raise CannotConvert(f"{spell.name}: the record has no components")
    rules = SpellRules(
        name=spell.name,
        level=spell.level,
        school=_enum(spell, "school", School, spell.school),
        classes=tuple(
            _enum(spell, "class", CharacterClass, name) for name in spell.classes
        ),
        casting_time=_field(spell, "casting time", CastingTime, spell.casting_time),
        range=_field(spell, "range", Range, spell.range),
        components=_field(spell, "components", Components, spell.components),
        duration=_field(spell, "duration", Duration, spell.duration),
        source=spell.source,
        description=spell.description,
        usage_tags=tuple(spell.usage_tags),  # type: ignore[arg-type]
        target=spell.target,
    )
    lines = [
        f"class {class_name(spell.name)}(ClassSpell):",
        f"    rules = {source_of(rules)}",
    ]
    blocks = spell.improved_description
    if blocks is not None:
        lines += [
            "",
            "    @property",
            "    def improved_description(self) -> list[Block]:",
            f"        return {source_of(blocks)}",
        ]
    effects = spell.combat_effects()
    if effects is not None:
        lines += [
            "",
            "    def combat_effects(",
            "        self, character: CharacterView | None = None",
            "    ) -> list[CombatEffect]:",
            f"        return {source_of(effects)}",
        ]
    return "\n".join(lines) + "\n"


def _enum(spell, what: str, enum_type, value):
    try:
        return enum_type(value)
    except ValueError:
        raise CannotConvert(
            f"{spell.name}: {what} {value!r} isn't a {enum_type.__name__}"
        ) from None


def _field(spell, what: str, field_type, text: str):
    """`text` read as a SpellFields dataclass."""
    try:
        return field_type.from_text(text)
    except ValueError:
        raise CannotConvert(f"{spell.name}: can't read the {what} {text!r}") from None


# ---------------------------------------------------------------------------
# Modules


def _module_docstring(level: int) -> str:
    what = "Cantrips" if level == 0 else f"Level {level} spells"
    return (
        f'"""{what} as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),\n'
        "which SpellFactory uses instead of their JSON records. Written by\n"
        "CharacterContent/Spells/SpellClassConverter.py; edit them by hand from\n"
        'then on: each class is its spell\'s one source."""\n'
    )


def _names_used(text: str) -> set[str]:
    """The importable names the code in `text` uses: names, not words in its
    strings (a description that says "Range" needs no import)."""
    used = {node.id for node in ast.walk(ast.parse(text)) if isinstance(node, ast.Name)}
    return used & set(_IMPORTS)


def add_to_module(path: Path, level: int, classes: dict[str, str]) -> str:
    """The module at `path` with `classes` ({class name: source}) added before
    its SPELLS list, its imports and SPELLS list brought up to date. What's
    there already, hand edits included, is kept."""
    text = (
        path.read_text(encoding="utf-8") if path.exists() else _module_docstring(level)
    )
    tree = ast.parse(text)
    existing = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    clash = existing & set(classes)
    if clash:
        raise ValueError(f"{path.name} already has class(es) {sorted(clash)}")
    lines = text.splitlines()
    # Drop the imports and the SPELLS list; they're written again below.
    drop: set[int] = set()
    kept_imports: dict[str, set[str]] = {}
    other_imports: list[str] = []
    for node in tree.body:
        span = range(node.lineno - 1, node.end_lineno or node.lineno)
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            kept_imports.setdefault(node.module, set()).update(
                alias.name for alias in node.names
            )
            drop.update(span)
        elif isinstance(node, ast.Import):
            other_imports.append("\n".join(lines[i] for i in span))
            drop.update(span)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SPELLS"
            for target in node.targets
        ):
            drop.update(span)
    body = "\n".join(line for i, line in enumerate(lines) if i not in drop)
    docstring_end = 0
    if tree.body and isinstance(tree.body[0], ast.Expr):
        docstring_end = tree.body[0].end_lineno or 0
    head = "\n".join(body.splitlines()[:docstring_end])
    rest = "\n".join(body.splitlines()[docstring_end:]).strip("\n")
    new_code = "\n\n\n".join(source.rstrip("\n") for source in classes.values())
    rest = f"{rest}\n\n\n{new_code}" if rest else new_code
    for name in _names_used(rest):
        kept_imports.setdefault(_IMPORTS[name], set()).add(name)
    import_lines = other_imports + [
        f"from {module} import {', '.join(sorted(names))}"
        for module, names in sorted(kept_imports.items())
    ]
    all_classes = sorted(existing | set(classes))
    spells = "SPELLS = [" + ", ".join(all_classes) + "]"
    return f"{head}\n\n" + "\n".join(import_lines) + f"\n\n\n{rest}\n\n\n{spells}\n"


def package_init() -> str:
    """SpellClasses/__init__.py: every level module there is, and the
    classes by spell name."""
    modules = sorted(
        (path.stem for path in CLASSES_DIR.glob("*.py") if path.stem != "__init__"),
        key=lambda stem: 0 if stem == "Cantrips" else int(stem.removeprefix("Level")),
    )
    imports = "\n".join(f"from . import {stem}" for stem in modules)
    # "(Cantrips, Level1, )" or "()": a tuple however many there are.
    listed = "".join(f"{stem}, " for stem in modules)
    return (
        '"""Spells written as classes, one module per level, and SPELL_CLASSES:\n'
        "each class by its spell's name, which SpellFactory uses instead of the\n"
        "spell's JSON record. Written by CharacterContent/Spells/\n"
        'SpellClassConverter.py; a module it doesn\'t know is not listed."""\n\n'
        f"{imports}\n"
        "from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell\n\n"
        f"MODULES: tuple = ({listed})\n\n"
        "SPELL_CLASSES: dict[str, type[ClassSpell]] = {}\n"
        "for _module in MODULES:\n"
        "    for _spell in _module.SPELLS:\n"
        "        if _spell.rules.name in SPELL_CLASSES:\n"
        '            raise ValueError(f"Two classes for the spell {_spell.rules.name!r}")\n'
        "        SPELL_CLASSES[_spell.rules.name] = _spell\n"
    )


# ---------------------------------------------------------------------------
# Companion files


def remove_entry(text: str, name: str) -> str:
    """`text`, a companion JSON file, without the top-level entry `name`,
    keeping the file's own layout: every top-level key starts a line, two
    spaces in."""
    key = f"  {json.dumps(name, ensure_ascii=False)}:"
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith('  "')]
    start = next((i for i in starts if lines[i].startswith(key)), None)
    if start is None:
        return text
    later = [i for i in starts if i > start]
    end = later[0] if later else len(lines) - 1 - lines[::-1].index("}")
    removed = lines[:start] + lines[end:]
    if not later:  # it was the last: the one before it ends the object now
        before = start - 1
        removed[before] = removed[before].rstrip(",")
    result = "\n".join(removed)
    expected = json.loads(text)
    expected.pop(name)
    if json.loads(result) != expected:
        raise ValueError(f"Removing {name!r} changed more than its entry")
    return result


def companion_paths(source_path: str) -> list[Path]:
    return [
        ROOT / (source_path[:-5] + "_extended.json"),
        ROOT / SpellFactory.improved_path(source_path),
        ROOT / SpellFactory.combat_effects_path(source_path),
    ]


# ---------------------------------------------------------------------------
# Checking


def differences(json_spell, class_spell) -> list[str]:
    """Where the class says something else than the JSON did."""
    checks = (
        "name",
        "level",
        "school",
        "classes",
        "casting_time_spec",
        "range_spec",
        "components_spec",
        "duration_spec",
        "description",
        "source",
        "usage_tags",
        "target",
        "improved_description",
        "duration_seconds",
        "is_concentration",
        "is_ritual",
        "range_feet",
        "school_enum",
        "has_verbal",
        "has_somatic",
        "has_material",
        "material_description",
    )
    found = [
        f"{field}: JSON {getattr(json_spell, field)!r}, class {getattr(class_spell, field)!r}"
        for field in checks
        if getattr(json_spell, field) != getattr(class_spell, field)
    ]
    if json_spell.combat_effects() != class_spell.combat_effects():
        found.append("combat_effects differ")
    return found


# ---------------------------------------------------------------------------


def winning_source(name: str) -> str:
    for path in SpellFactory.json_paths:
        with open(ROOT / path, encoding="utf-8") as f:
            if name in json.load(f):
                return path
    raise ValueError(f"No source has the spell {name!r}")


def chosen(args) -> list[DataSpell]:
    data = SpellFactory._load_json()
    spells = [DataSpell(record) for record in data.values()]
    if args.name:
        unknown = set(args.name) - set(data)
        if unknown:
            sys.exit(f"Unknown spell(s): {sorted(unknown)}")
        spells = [s for s in spells if s.name in args.name]
    if args.described:
        spells = [s for s in spells if s.combat_effects() is not None]
    if args.level is not None:
        spells = [s for s in spells if s.level == args.level]
    return sorted(spells, key=lambda s: (s.level, s.name))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--name", action="append", help="repeatable")
    parser.add_argument("--level", type=int)
    parser.add_argument("--described", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-json", action="store_true")
    args = parser.parse_args()
    if not (args.name or args.described or args.level is not None or args.all):
        parser.error("say which spells: --name, --described, --level or --all")

    from CharacterContent.Spells.SpellClasses import SPELL_CLASSES

    todo = [s for s in chosen(args) if s.name not in SPELL_CLASSES]
    skipped = len(chosen(args)) - len(todo)
    if skipped:
        print(f"{skipped} spell(s) have a class already: skipped")
    if not todo:
        print("Nothing to convert.")
        return 0
    by_level: dict[int, dict[str, str]] = {}
    left = []
    for spell in todo:
        try:
            source = class_source(spell)
        except CannotConvert as reason:
            left.append(str(reason))
            continue
        by_level.setdefault(spell.level, {})[class_name(spell.name)] = source
    for reason in left:
        print("LEFT AS JSON", reason)
    todo = [s for s in todo if class_name(s.name) in by_level.get(s.level, {})]
    if not todo:
        print("Nothing to convert.")
        return 0
    if args.dry_run:
        for classes in by_level.values():
            for source in classes.values():
                print(source)
        print(f"{len(todo)} class(es), nothing written")
        return 0

    CLASSES_DIR.mkdir(exist_ok=True)
    before = {
        path: path.read_text(encoding="utf-8") for path in CLASSES_DIR.glob("*.py")
    }
    written = []
    for level, classes in sorted(by_level.items()):
        path = CLASSES_DIR / f"{module_name(level)}.py"
        path.write_text(
            add_to_module(path, level, classes), encoding="utf-8", newline="\n"
        )
        written.append(path)
    init = CLASSES_DIR / "__init__.py"
    init.write_text(package_init(), encoding="utf-8", newline="\n")
    written.append(init)
    subprocess.run(
        [sys.executable, "-m", "black", "-q", *map(str, written)], check=True
    )

    # Check every class against the JSON it came from, before the JSON goes.
    for name in [m for m in list(sys.modules) if m.startswith(PACKAGE)]:
        del sys.modules[name]
    try:
        classes_module = importlib.import_module(PACKAGE)
        problems = []
        for spell in todo:
            made = classes_module.SPELL_CLASSES[spell.name]()
            problems += [f"{spell.name}: {d}" for d in differences(spell, made)]
    except Exception as error:  # a class that doesn't even import
        problems = [f"the classes don't import: {error!r}"]
    if problems:
        for path in written:
            if path in before:
                path.write_text(before[path], encoding="utf-8", newline="\n")
            else:
                path.unlink()
        for problem in problems:
            print("PROBLEM", problem)
        print("Nothing kept: the classes were taken back out.")
        return 1

    if not args.keep_json:
        for spell in todo:
            for path in companion_paths(winning_source(spell.name)):
                if not path.exists():
                    continue
                text = path.read_text(encoding="utf-8")
                new = remove_entry(text, spell.name)
                if new != text:
                    path.write_text(new, encoding="utf-8", newline="")
    for path in written:
        print(f"wrote {path.relative_to(ROOT).as_posix()}")
    print(f"{len(todo)} spell(s) converted and checked against their JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
