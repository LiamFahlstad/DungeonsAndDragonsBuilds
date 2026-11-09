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
    python -m CharacterContent.Spells.SpellClassConverter --drift   # after a re-scrape
    python -m CharacterContent.Spells.SpellClassConverter --accept Fireball   # once merged

Each class is stamped with the scraped record it was written from
(`converted_from`, a hash of the record). A re-scrape that changes the
record doesn't reach the class; --drift lists those classes and how their
rules now differ from the record, for a person to merge by hand, and
--accept stamps a class with its record as it is now.

A spell that already has a class is skipped: the class may have been edited
by hand since. Each class is checked before anything is written to the
companion files: built by the factory, it must give the same rules, tags,
target, improved description and combat effects as the JSON did. The casting
time, range, components and duration are compared as what they mean
(SpellFields), not as text: the class writes them in the 2024 wording.

The spell-mechanics skill's script uses it as a library: convert() with
combat effects of its own writes a spell's class with those instead of its
record's, and set_combat_effects() gives a class that exists a
combat_effects() method (a new one, or in place of the one it has). Both
check what they wrote the same way, and put every file back if it's wrong.
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory  # noqa: E402
from CharacterContent.Spells.SpellFactory.ClassSpell import (  # noqa: E402
    RecordStamp,
    SpellRules,
)
from CharacterContent.Spells.SpellFactory.Enums import School  # noqa: E402
from CharacterContent.Spells.SpellFactory.SpellFields import (  # noqa: E402
    CastingTime,
    Components,
    Duration,
    Range,
)
from Core.Definitions import CharacterClass, Condition  # noqa: E402
from Model.Content.CombatEffect import CombatEffect  # noqa: E402

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
    "EffectRoll": "Model.Content.CombatEffect",
    "TurnEdge": "Model.Content.CombatEffect",
    "TurnOf": "Model.Content.CombatEffect",
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
    "RecordStamp": "CharacterContent.Spells.SpellFactory.ClassSpell",
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


def class_source(spell: DataSpell, effects: Optional[list[CombatEffect]] = None) -> str:
    """The class for `spell`, a JSON spell with its companions merged;
    given `effects`, its combat_effects() gives those instead of what the
    record says."""
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
    stamp = stamp_for(spell.name)
    if stamp is not None:
        lines.append(f"    converted_from = {source_of(stamp)}")
    blocks = spell.improved_description
    if blocks is not None:
        lines += [
            "",
            "    @property",
            "    def improved_description(self) -> list[Block]:",
            f"        return {source_of(blocks)}",
        ]
    if effects is None:
        effects = spell.combat_effects()
    if effects is not None:
        lines += [""] + effects_method(effects)
    return "\n".join(lines) + "\n"


def effects_method(effects: list[CombatEffect]) -> list[str]:
    """The lines of a class's combat_effects() method giving `effects`."""
    return [
        "    def combat_effects(",
        "        self, character: CharacterView | None = None",
        "    ) -> list[CombatEffect]:",
        f"        return {source_of(effects)}",
    ]


def with_effects_method(text: str, class_name: str, effects: list[CombatEffect]) -> str:
    """`text`, a SpellClasses module, with the class `class_name`'s
    combat_effects() giving `effects`: the method it has is replaced (with
    any decorators), or a new one is added at the end of the class."""
    return with_class_member(
        text, class_name, "combat_effects", [""] + effects_method(effects)
    )


def with_stamp(text: str, class_name: str, stamp: RecordStamp) -> str:
    """`text` with the class `class_name`'s converted_from set to `stamp`:
    in place of the one it has, or right after its rules."""
    line = f"    converted_from = {source_of(stamp)}"
    return with_class_member(text, class_name, "converted_from", [line], "rules")


def with_class_member(
    text: str,
    class_name: str,
    member: str,
    lines_to_add: list[str],
    after: Optional[str] = None,
) -> str:
    """`text`, a SpellClasses module, with the class `class_name`'s method
    or attribute `member` replaced by `lines_to_add` (its decorators too).
    One it doesn't have is added after the member `after`, or at the end of
    the class. A leading "" in `lines_to_add` is the blank line before a new
    member; replacing one keeps the spacing it had."""
    tree = ast.parse(text)
    node = next(
        (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name),
        None,
    )
    if node is None:
        raise ValueError(f"The module has no class {class_name!r}")
    lines = text.splitlines()
    old = _member(node, member)
    if old is not None:
        decorators = getattr(old, "decorator_list", [])
        first = min([old.lineno] + [d.lineno for d in decorators])
        new = lines_to_add[1:] if lines_to_add[:1] == [""] else lines_to_add
        lines[first - 1 : old.end_lineno] = new
    else:
        anchor = _member(node, after) if after else None
        end = (anchor or node).end_lineno or node.lineno
        lines[end:end] = lines_to_add
    return "\n".join(lines) + "\n"


def _member(node: ast.ClassDef, name: Optional[str]) -> Optional[ast.stmt]:
    """The statement in the class body that defines `name`: a method, or an
    assignment to it."""
    for statement in node.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if statement.name == name:
                return statement
        elif isinstance(statement, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in statement.targets):
                return statement
        elif isinstance(statement, ast.AnnAssign):
            if isinstance(statement.target, ast.Name) and statement.target.id == name:
                return statement
    return None


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
    return module_with(text, classes)


def module_with(text: str, classes: dict[str, str]) -> str:
    """add_to_module() on a module's text. With no `classes`, the module's
    imports and SPELLS list brought up to date with what its code uses."""
    tree = ast.parse(text)
    existing = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    clash = existing & set(classes)
    if clash:
        raise ValueError(f"The module already has class(es) {sorted(clash)}")
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
    if new_code:
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


def differences(
    json_spell, class_spell, effects: Optional[list[CombatEffect]] = None
) -> list[str]:
    """Where the class says something else than the JSON did; given
    `effects`, its combat effects are checked against those instead."""
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
    wanted = json_spell.combat_effects() if effects is None else effects
    if wanted != class_spell.combat_effects():
        found.append("combat_effects differ")
    return found


# ---------------------------------------------------------------------------


def winning_source(name: str) -> str:
    found = scraped_record(name)
    if found is None:
        raise ValueError(f"No source has the spell {name!r}")
    return found[0]


_RAW_SOURCES: dict[str, dict] = {}


def scraped_record(name: str) -> Optional[tuple[str, dict]]:
    """The source path whose record SpellFactory uses for the spell, and
    that record as the scraped file has it (no companions merged in), or
    None for a spell no source has. The files are read once."""
    for path in SpellFactory.json_paths:
        if path not in _RAW_SOURCES:
            with open(ROOT / path, encoding="utf-8") as f:
                _RAW_SOURCES[path] = json.load(f)
        if name in _RAW_SOURCES[path]:
            return path, _RAW_SOURCES[path][name]
    return None


def stamp_for(name: str) -> Optional[RecordStamp]:
    """The stamp of the spell's scraped record as it is now."""
    found = scraped_record(name)
    if found is None:
        return None
    path, record = found
    return RecordStamp.of(Path(path).name, record)


# ---------------------------------------------------------------------------
# Drift: a re-scrape that changed a converted spell's record


_NOT_RULES = ("usage_tags", "target", "improved_description", "combat_effects")


def drifted() -> list[tuple[str, str]]:
    """Each class whose stamp isn't its scraped record's as it is now, and
    why: the record changed (or another source wins now), it's gone, or the
    class has no stamp. A class with neither (homebrew) is fine."""
    from CharacterContent.Spells.SpellClasses import SPELL_CLASSES

    found = []
    for name, spell_class in sorted(SPELL_CLASSES.items()):
        stamp, now = spell_class.converted_from, stamp_for(name)
        if stamp == now:
            continue
        if now is None:
            reason = f"its record in {stamp.source if stamp else '?'} is gone"
        elif stamp is None:
            reason = f"no converted_from stamp; its record is in {now.source}"
        elif stamp.source != now.source:
            reason = f"converted from {stamp.source}, but {now.source} wins now"
        else:
            reason = f"its record in {now.source} changed since it was converted"
        found.append((name, reason))
    return found


def drift_report(name: str) -> list[str]:
    """Where the spell's class and its scraped record now disagree on the
    rules (casting time, range and so on by meaning): what to merge by hand.
    Companion data (tags, improved description, effects) isn't compared."""
    from CharacterContent.Spells.SpellClasses import SPELL_CLASSES

    found = scraped_record(name)
    if found is None:
        return []
    record = DataSpell(dict(found[1]))
    return [
        difference
        for difference in differences(record, SPELL_CLASSES[name]())
        if not difference.startswith(_NOT_RULES)
    ]


def accept_records(names: list[str]) -> "Result":
    """Stamp each named class with its scraped record as it is now: after a
    person has merged what the record changed into the class (or decided
    the class is right as it is)."""
    from CharacterContent.Spells.SpellClasses import SPELL_CLASSES

    unknown = sorted(set(names) - set(SPELL_CLASSES))
    if unknown:
        raise ValueError(f"No class for the spell(s) {unknown}")
    stamps = {name: stamp_for(name) for name in names}
    missing = sorted(name for name, stamp in stamps.items() if stamp is None)
    if missing:
        raise ValueError(f"No scraped record to stamp for {missing}")
    texts: dict[Path, str] = {}
    for name, stamp in stamps.items():
        spell_class = SPELL_CLASSES[name]
        path = CLASSES_DIR / f"{spell_class.__module__.rsplit('.', 1)[-1]}.py"
        text = texts.get(path) or path.read_text(encoding="utf-8")
        texts[path] = with_stamp(text, spell_class.__name__, stamp)  # type: ignore[arg-type]
    texts = {path: module_with(text, {}) for path, text in texts.items()}

    def check(spell_classes: dict) -> list[str]:
        return [
            f"{name}: stamp not written"
            for name, stamp in stamps.items()
            if spell_classes[name].converted_from != stamp
        ]

    result = Result()
    result.problems, result.written = _write_checked(texts, check)
    if not result.problems:
        result.done = list(names)
    return result


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


@dataclass
class Result:
    """What convert() or set_combat_effects() did: the spells it wrote, those
    it left as JSON and why, and what was wrong (then nothing was kept)."""

    done: list[str] = field(default_factory=list)
    left: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    written: list[Path] = field(default_factory=list)


def convert(
    spells: list[DataSpell],
    effects: Optional[dict[str, list[CombatEffect]]] = None,
    keep_json: bool = False,
) -> Result:
    """Write a class for each of `spells` (JSON spells without one), check
    each gives what its JSON gave, then take the spells out of the companion
    files (unless `keep_json`). A spell named in `effects` gets those combat
    effects instead of its record's, and is checked against them. A spell
    the classes can't say (CannotConvert) is left as JSON, in `left`."""
    effects = effects or {}
    result = Result()
    by_level: dict[int, dict[str, str]] = {}
    for spell in spells:
        try:
            source = class_source(spell, effects.get(spell.name))
        except CannotConvert as reason:
            result.left.append(str(reason))
            continue
        by_level.setdefault(spell.level, {})[class_name(spell.name)] = source
    todo = [s for s in spells if class_name(s.name) in by_level.get(s.level, {})]
    if not todo:
        return result

    CLASSES_DIR.mkdir(exist_ok=True)
    texts = {
        CLASSES_DIR
        / f"{module_name(level)}.py": add_to_module(
            CLASSES_DIR / f"{module_name(level)}.py", level, classes
        )
        for level, classes in sorted(by_level.items())
    }

    def check(spell_classes: dict) -> list[str]:
        problems = []
        for spell in todo:
            made = spell_classes[spell.name]()
            found = differences(spell, made, effects.get(spell.name))
            problems += [f"{spell.name}: {d}" for d in found]
        return problems

    result.problems, result.written = _write_checked(texts, check, new_init=True)
    if result.problems:
        return result
    result.done = [spell.name for spell in todo]
    if not keep_json:
        for spell in todo:
            for path in companion_paths(winning_source(spell.name)):
                if not path.exists():
                    continue
                text = path.read_text(encoding="utf-8")
                new = remove_entry(text, spell.name)
                if new != text:
                    path.write_text(new, encoding="utf-8", newline="")
    return result


def set_combat_effects(effects: dict[str, list[CombatEffect]]) -> Result:
    """Give each spell named in `effects`, which must have a class, a
    combat_effects() method returning those effects: in place of the one its
    class has, or a new one. Checked as convert() checks: if any class then
    gives something else, every file is put back."""
    from CharacterContent.Spells.SpellClasses import SPELL_CLASSES

    unknown = sorted(set(effects) - set(SPELL_CLASSES))
    if unknown:
        raise ValueError(f"No class for the spell(s) {unknown}")
    texts: dict[Path, str] = {}
    for name, spell_effects in effects.items():
        spell_class = SPELL_CLASSES[name]
        path = CLASSES_DIR / f"{spell_class.__module__.rsplit('.', 1)[-1]}.py"
        text = texts.get(path) or path.read_text(encoding="utf-8")
        texts[path] = with_effects_method(text, spell_class.__name__, spell_effects)
    texts = {path: module_with(text, {}) for path, text in texts.items()}

    def check(spell_classes: dict) -> list[str]:
        return [
            f"{name}: combat_effects differ"
            for name, wanted in effects.items()
            if spell_classes[name]().combat_effects() != wanted
        ]

    result = Result()
    result.problems, result.written = _write_checked(texts, check)
    if not result.problems:
        result.done = list(effects)
    return result


def _write_checked(
    texts: dict[Path, str],
    check: Callable[[dict], list[str]],
    new_init: bool = False,
) -> tuple[list[str], list[Path]]:
    """Write each module's new text (and, with `new_init`, the package's
    __init__.py listing the modules), format them with Black, import the
    package afresh and run `check` on its SPELL_CLASSES. On a problem, or a
    module that doesn't import, every file is put back as it was. Returns
    the problems and the files written."""
    before = {
        path: path.read_text(encoding="utf-8") for path in CLASSES_DIR.glob("*.py")
    }
    written = []
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8", newline="\n")
        written.append(path)
    if new_init:
        init = CLASSES_DIR / "__init__.py"
        init.write_text(package_init(), encoding="utf-8", newline="\n")
        written.append(init)
    # Not check=True: a module Black can't parse fails the import below,
    # which puts the files back.
    subprocess.run([sys.executable, "-m", "black", "-q", *map(str, written)])
    _forget_classes()
    try:
        problems = check(importlib.import_module(PACKAGE).SPELL_CLASSES)
    except Exception as error:  # a class that doesn't even import
        problems = [f"the classes don't import: {error!r}"]
    if problems:
        for path in written:
            if path in before:
                path.write_text(before[path], encoding="utf-8", newline="\n")
            else:
                path.unlink()
        _forget_classes()
    return problems, written


def _forget_classes() -> None:
    """Drop the imported SpellClasses modules, so the next import reads the
    files as they are now."""
    for name in [m for m in list(sys.modules) if m.startswith(PACKAGE)]:
        del sys.modules[name]


def _print_drift() -> int:
    found = drifted()
    for name, reason in found:
        print(f"{name}: {reason}")
        report = drift_report(name)
        for difference in report:
            print(f"    {difference}")
        if not report:
            print("    the rules still agree (by meaning); only the stamp is old")
    if found:
        print(
            f"{len(found)} class(es) to check: merge what changed into each"
            " class by hand, then --accept it"
        )
    else:
        print("Every class matches the record it was converted from.")
    return 1 if found else 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--name", action="append", help="repeatable")
    parser.add_argument("--level", type=int)
    parser.add_argument("--described", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-json", action="store_true")
    parser.add_argument(
        "--drift",
        action="store_true",
        help="list classes whose scraped record changed, and what to merge",
    )
    parser.add_argument(
        "--accept",
        action="append",
        metavar="SPELL",
        help="stamp the class with its record as it is now (repeatable)",
    )
    args = parser.parse_args()
    if args.drift:
        return _print_drift()
    if args.accept:
        result = accept_records(args.accept)
        for problem in result.problems:
            print("PROBLEM", problem)
        for name in result.done:
            print(f"{name}: stamped with its record as it is now")
        return 1 if result.problems else 0
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
    if args.dry_run:
        count = 0
        for spell in todo:
            try:
                print(class_source(spell))
                count += 1
            except CannotConvert as reason:
                print("LEFT AS JSON", reason)
        print(f"{count} class(es), nothing written")
        return 0

    result = convert(todo, keep_json=args.keep_json)
    for reason in result.left:
        print("LEFT AS JSON", reason)
    if result.problems:
        for problem in result.problems:
            print("PROBLEM", problem)
        print("Nothing kept: the classes were taken back out.")
        return 1
    if not result.done:
        print("Nothing to convert.")
        return 0
    for path in result.written:
        print(f"wrote {path.relative_to(ROOT).as_posix()}")
    print(f"{len(result.done)} spell(s) converted and checked against their JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
