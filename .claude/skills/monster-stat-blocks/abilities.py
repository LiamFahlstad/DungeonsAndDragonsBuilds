"""Print the structured MonsterAbility subclasses, read live from Model/Creatures/MonsterAbilities.py.

Usage (from the repo root):
    python .claude/skills/monster-stat-blocks/abilities.py                # every subclass
    python .claude/skills/monster-stat-blocks/abilities.py MeleeAttack    # just these

For each subclass: its constructor fields with defaults, whether `name` is derived (then you
must not pass `name=`), its docstring, and the text it generates. In the generated text, string
fields show as <field> so you can see where each one lands. Numbers and enums use their defaults.
Because this reads the code itself, it is always current - prefer it over any copied reference.
"""

import dataclasses
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from Model.Creatures import MonsterAbilities  # noqa: E402

Base = MonsterAbilities.MonsterAbility


def subclasses() -> list[type]:
    found = [
        obj
        for _, obj in inspect.getmembers(MonsterAbilities, inspect.isclass)
        if issubclass(obj, Base) and obj is not Base and obj.__module__ == MonsterAbilities.__name__
    ]
    return sorted(found, key=lambda cls: inspect.getsourcelines(cls)[1])


def field_text(field: dataclasses.Field) -> str:
    if field.default is not dataclasses.MISSING:
        default = field.default
        shown = f"{type(default).__name__}.{default.name}" if hasattr(default, "name") and hasattr(default, "value") else repr(default)
        return f"{field.name}={shown}"
    return field.name


def example(cls: type) -> str:
    kwargs = {}
    for field in dataclasses.fields(cls):
        if not field.init:
            continue
        if field.type in (str, "str"):
            kwargs[field.name] = f"<{field.name}>"
        elif field.default is dataclasses.MISSING:
            return "(needs non-string required fields; see the source)"
    try:
        instance = cls(**kwargs)
    except Exception as error:  # noqa: BLE001 - show why, don't crash the listing
        return f"(could not build an example: {error})"
    return f"name: {instance.name!r}\n    text: {instance.description!r}"


def describe(cls: type) -> str:
    fields = [f for f in dataclasses.fields(cls) if f.init]
    name_derived = not next(f for f in dataclasses.fields(cls) if f.name == "name").init
    doc = inspect.getdoc(cls) or ""
    lines = [
        f"## {cls.__name__}" + ("  (name is derived: don't pass name=)" if name_derived else ""),
        f"  {cls.__name__}({', '.join(field_text(f) for f in fields)})",
    ]
    if doc:
        lines.append("  " + doc.replace("\n", "\n  "))
    lines.append("  example (string fields as <field>):\n    " + example(cls))
    return "\n".join(lines)


def main(names: list[str]) -> int:
    classes = subclasses()
    if names:
        by_name = {cls.__name__: cls for cls in classes}
        missing = [n for n in names if n not in by_name]
        if missing:
            print(f"unknown: {', '.join(missing)}. Known: {', '.join(by_name)}")
            return 1
        classes = [by_name[n] for n in names]
    print("\n\n".join(describe(cls) for cls in classes))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
