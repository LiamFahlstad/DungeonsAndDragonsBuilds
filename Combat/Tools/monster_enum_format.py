"""Shared source-text formatting helpers for monster stat-block fields.

Used by both `generate_monsters.py` (fresh codegen from monsters_raw.json) and
`migrate_monster_enums.py` (one-time migration of already-generated files), so
both paths always emit the identical enum/dataclass-based Python source.

Each `format_*` function takes plain-literal input (str/int/dict/list — the
shape you'd get from raw scraped JSON or from `ast.literal_eval`-ing existing
generated source) and returns source text to splice into a monster class body.
Functions that can fail to map a value onto a known enum also return the list
of raw strings they couldn't confidently map, so callers can flag them for
manual review instead of silently losing information.
"""

import re

_ABILITY_ABBR_TO_ENUM = {
    "str": "STRENGTH",
    "dex": "DEXTERITY",
    "con": "CONSTITUTION",
    "int": "INTELLIGENCE",
    "wis": "WISDOM",
    "cha": "CHARISMA",
}

_SKILL_NAME_TO_ENUM = {
    "acrobatics": "ACROBATICS",
    "animal handling": "ANIMAL_HANDLING",
    "arcana": "ARCANA",
    "athletics": "ATHLETICS",
    "deception": "DECEPTION",
    "history": "HISTORY",
    "insight": "INSIGHT",
    "intimidation": "INTIMIDATION",
    "investigation": "INVESTIGATION",
    "medicine": "MEDICINE",
    "nature": "NATURE",
    "perception": "PERCEPTION",
    "performance": "PERFORMANCE",
    "persuasion": "PERSUASION",
    "religion": "RELIGION",
    "sleight of hand": "SLEIGHT_OF_HAND",
    "stealth": "STEALTH",
    "survival": "SURVIVAL",
}

_DAMAGE_TYPE_TO_ENUM = {
    "acid": "ACID",
    "bludgeoning": "BLUDGEONING",
    "cold": "COLD",
    "fire": "FIRE",
    "force": "FORCE",
    "lightning": "LIGHTNING",
    "necrotic": "NECROTIC",
    "piercing": "PIERCING",
    "poison": "POISON",
    "psychic": "PSYCHIC",
    "radiant": "RADIANT",
    "slashing": "SLASHING",
    "thunder": "THUNDER",
}

_CONDITION_NAME_TO_ENUM = {
    "blinded": "BLINDED",
    "bloodied": "BLOODIED",
    "charmed": "CHARMED",
    "concentrating": "CONCENTRATING",
    "deafened": "DEAFENED",
    "exhaustion": "EXHAUSTION",
    "frightened": "FRIGHTENED",
    "grappled": "GRAPPLED",
    "incapacitated": "INCAPACITATED",
    "invisible": "INVISIBLE",
    "paralyzed": "PARALYZED",
    "petrified": "PETRIFIED",
    "poisoned": "POISONED",
    "prone": "PRONE",
    "restrained": "RESTRAINED",
    "stunned": "STUNNED",
    "unconscious": "UNCONSCIOUS",
}


def format_ability_scores(d: dict) -> str:
    """{"Str": 20, ...} -> '{Ability.STRENGTH.short_name: 20, ...}'."""
    if not d:
        return "{}"
    items = []
    for key, value in d.items():
        enum_name = _ABILITY_ABBR_TO_ENUM.get(str(key).strip().lower())
        if enum_name:
            items.append(f"Ability.{enum_name}.short_name: {value!r}")
        else:
            items.append(f"{key!r}: {value!r}")
    return "{" + ", ".join(items) + "}"


def format_skills(d: dict) -> tuple[str, list[str]]:
    """{"Perception": 5} -> ('{Skill.PERCEPTION: 5}', []); unmapped names are returned separately."""
    if not d:
        return "{}", []
    items = []
    unmapped = []
    for key, value in d.items():
        enum_name = _SKILL_NAME_TO_ENUM.get(str(key).strip().lower())
        if enum_name:
            items.append(f"Skill.{enum_name}: {value!r}")
        else:
            items.append(f"{key!r}: {value!r}")
            unmapped.append(str(key))
    return "{" + ", ".join(items) + "}", unmapped


def _parse_damage_phrase(phrase: str) -> tuple[list[str], str]:
    """'Bludgeoning, Piercing, and Slashing from Nonmagical Attacks'
    -> (['BLUDGEONING', 'PIERCING', 'SLASHING'], 'from Nonmagical Attacks').
    Returns ([], phrase) if the phrase doesn't cleanly resolve to known damage types.
    """
    phrase = phrase.strip()
    note = ""
    main = phrase
    m = re.search(r"\bfrom\b", phrase, flags=re.IGNORECASE)
    if m:
        main = phrase[: m.start()].strip().rstrip(",")
        note = phrase[m.start():].strip()
    fragments = [f.strip() for f in re.split(r",|\band\b", main) if f.strip()]
    if not fragments:
        return [], phrase
    types = []
    for frag in fragments:
        enum_name = _DAMAGE_TYPE_TO_ENUM.get(frag.lower())
        if enum_name is None:
            return [], phrase
        types.append(enum_name)
    return types, note


def format_damage_entries(lst: list) -> tuple[str, list[str]]:
    """List of raw phrases -> source text for a list[DamageTypeEntry] literal.
    Phrases that can't be parsed become DamageTypeEntry(damage_types=[], note=<original text>)
    and are also returned in the unparsed list for manual review."""
    if not lst:
        return "[]", []
    entries = []
    unparsed = []
    for phrase in lst:
        types, note = _parse_damage_phrase(str(phrase))
        if types:
            types_src = ", ".join(f"DamageType.{t}" for t in types)
            entries.append(f"DamageTypeEntry(damage_types=[{types_src}], note={note!r})")
        else:
            entries.append(f"DamageTypeEntry(damage_types=[], note={phrase!r})")
            unparsed.append(str(phrase))
    inner = ",\n                ".join(entries)
    return "[\n                " + inner + ",\n            ]", unparsed


def format_condition_list(lst: list) -> tuple[str, list[str]]:
    """['Charmed', 'Exhaustion'] -> ('[Condition.CHARMED, Condition.EXHAUSTION]', [])."""
    if not lst:
        return "[]", []
    items = []
    unmapped = []
    for cond in lst:
        enum_name = _CONDITION_NAME_TO_ENUM.get(str(cond).strip().lower())
        if enum_name:
            items.append(f"Condition.{enum_name}")
        else:
            items.append(repr(cond))
            unmapped.append(str(cond))
    return "[" + ", ".join(items) + "]", unmapped


def format_ability_list(abilities: list) -> str:
    """[{"name": ..., "description": ...}] -> '[MonsterAbility(name=..., description=...), ...]'."""
    if not abilities:
        return "[]"
    lines = ["["]
    for ab in abilities:
        name = ab.get("name", "")
        desc = ab.get("description", "")
        lines.append(f"        MonsterAbility(name={name!r}, description={desc!r}),")
    lines.append("    ]")
    return "\n    ".join(lines)
