"""Generates Spells/SpellLists.py from SpellFactory's merged spell data.

SpellFactory merges Spells/spells_dnd2024.json, spells_aidedd.json, and
spells_dnd5e.json in that priority order. Run directly
(`python Spells/SpellGenerator.py`) whenever any of those files change to
regenerate the per-class and per-school spell-name enums.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Spells.SpellFactory import SpellFactory

OUTPUT_PY = "Spells/SpellLists.py"

# Order classes/schools are emitted in, purely for readable diffs.
CLASS_ORDER = [
    "Sorcerer",
    "Artificer",
    "Wizard",
    "Bard",
    "Cleric",
    "Druid",
    "Paladin",
    "Ranger",
    "Warlock",
]
SCHOOL_ORDER = [
    "Abjuration",
    "Conjuration",
    "Divination",
    "Enchantment",
    "Evocation",
    "Illusion",
    "Necromancy",
    "Transmutation",
]
LEVELS = range(10)


def member_name(spell_name: str) -> str:
    """Convert a spell name into a SCREAMING_SNAKE_CASE enum member name.

    Examples:
        Acid Splash -> ACID_SPLASH
        Dragon's Breath -> DRAGONS_BREATH
        Blindness/Deafness -> BLINDNESS_DEAFNESS
    """
    cleaned = re.sub(r"['’]", "", spell_name)
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", cleaned).strip("_")
    return cleaned.upper()


def build_enum_source(class_name: str, spell_names: list[str]) -> str:
    if not spell_names:
        return f"class {class_name}(str, Enum):\n    pass\n"
    lines = [f"class {class_name}(str, Enum):"]
    for name in spell_names:
        lines.append(f'    {member_name(name)} = "{name}"')
    return "\n".join(lines) + "\n"


def main():
    spells = SpellFactory.all_spells()

    by_class_level: dict[tuple[str, int], list[str]] = {}
    by_school_level: dict[tuple[str, int], list[str]] = {}
    for spell in spells:
        level = spell.level
        for cls in spell.classes:
            by_class_level.setdefault((cls, level), []).append(spell.name)
        by_school_level.setdefault((spell.school, level), []).append(spell.name)

    output = ["from enum import Enum\n\n"]

    # Class-based enums: only emitted when at least one spell exists for that
    # class/level combination (half-casters like Paladin/Ranger never get
    # cantrips or spells above 5th level, so those enums simply don't exist).
    for cls in CLASS_ORDER:
        for level in LEVELS:
            names = sorted(by_class_level.get((cls, level), []))
            if not names:
                continue
            output.append(build_enum_source(f"{cls}Level{level}Spells", names))
            output.append("\n")

    # School-based enums: always emitted for all 10 levels, even if empty,
    # since callers build "spells up to level N" unions across every level.
    for school in SCHOOL_ORDER:
        for level in LEVELS:
            names = sorted(by_school_level.get((school, level), []))
            output.append(build_enum_source(f"{school}Level{level}Spells", names))
            output.append("\n")

    Path(OUTPUT_PY).write_text("".join(output).rstrip() + "\n", encoding="utf-8")
    print(f"Generated enums for {len(spells)} spells -> {OUTPUT_PY}")


if __name__ == "__main__":
    main()
