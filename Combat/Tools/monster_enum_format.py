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


_SIZE_NAMES = ["Gargantuan", "Huge", "Large", "Medium", "Small", "Tiny"]
_SIZE_RE = re.compile(r"^(" + "|".join(_SIZE_NAMES) + r")\b", re.IGNORECASE)
_SIZE_OR_QUALIFIER_RE = re.compile(
    r"^\s+or\s+(" + "|".join(_SIZE_NAMES) + r"|Smaller|Larger)\b", re.IGNORECASE
)

_ALIGNMENT_TO_ENUM = {
    "lawful good": "LAWFUL_GOOD",
    "neutral good": "NEUTRAL_GOOD",
    "chaotic good": "CHAOTIC_GOOD",
    "lawful neutral": "LAWFUL_NEUTRAL",
    "neutral": "NEUTRAL",
    "chaotic neutral": "CHAOTIC_NEUTRAL",
    "lawful evil": "LAWFUL_EVIL",
    "neutral evil": "NEUTRAL_EVIL",
    "chaotic evil": "CHAOTIC_EVIL",
    "unaligned": "UNALIGNED",
    "any alignment": "ANY_ALIGNMENT",
}


def parse_monster_type(raw: str) -> tuple[str, str, str, list[str]]:
    """'Medium Dragon (Metallic), Chaotic Good' -> ('MEDIUM', 'Dragon (Metallic)', 'CHAOTIC_GOOD', flags).

    size/alignment are Size/Alignment enum *names* (or "" if unparseable);
    flags lists anything that couldn't be cleanly resolved (compound sizes like
    "Huge or Gargantuan" are reduced to their first/primary size and flagged).
    """
    raw = raw.strip()
    if not raw:
        return "", "", "", []
    flags = []
    if "," in raw:
        type_and_size, _, alignment_part = raw.rpartition(",")
    else:
        type_and_size, alignment_part = raw, ""
    type_and_size = type_and_size.strip()
    alignment_part = alignment_part.strip()

    alignment_name = _ALIGNMENT_TO_ENUM.get(alignment_part.lower(), "")
    if not alignment_name and alignment_part:
        flags.append(f"unmapped alignment: {alignment_part!r}")

    m = _SIZE_RE.match(type_and_size)
    if not m:
        flags.append(f"no leading size in: {type_and_size!r}")
        return "", type_and_size, alignment_name, flags
    size_name = m.group(1).upper()
    rest = type_and_size[m.end():]
    m2 = _SIZE_OR_QUALIFIER_RE.match(rest)
    if m2:
        flags.append(f"compound size reduced to {size_name}: {type_and_size!r}")
        rest = rest[m2.end():]
    return size_name, rest.strip(), alignment_name, flags


_SPEED_BARE_RE = re.compile(r"^(\d+)\s*ft\.?$", re.IGNORECASE)
_SPEED_KEYWORD_RE = re.compile(r"^(climb|fly|swim|burrow)\s+(\d+)\s*ft\.?\s*(\(.*\))?$", re.IGNORECASE)


def parse_speed(raw: str) -> tuple[int | None, int | None, int | None, str, list[str]]:
    """'40 ft., climb 40 ft., fly 80 ft.' -> (40, 80, 40, '', []).
    Anything that doesn't fit (garbage scrape fragments, an unrecognized
    segment, swim/burrow speeds) is preserved verbatim in the returned note
    text rather than dropped, and flagged for review."""
    raw = raw.strip().rstrip(",").strip()
    flags = []
    if not raw:
        return None, None, None, "", flags
    if not re.match(r"^\d", raw):
        flags.append(f"unparseable speed text (kept as note): {raw!r}")
        return None, None, None, raw, flags

    segments = [s.strip() for s in raw.split(",") if s.strip()]
    ground = fly = climb = None
    notes = []
    for i, seg in enumerate(segments):
        m_bare = _SPEED_BARE_RE.match(seg)
        m_kw = _SPEED_KEYWORD_RE.match(seg)
        if m_bare and i == 0:
            ground = int(m_bare.group(1))
        elif m_kw:
            kind = m_kw.group(1).lower()
            value = int(m_kw.group(2))
            paren_note = m_kw.group(3)
            if kind == "climb":
                climb = value
            elif kind == "fly":
                fly = value
            else:
                notes.append(f"{kind} {value} ft.")
            if paren_note:
                notes.append(paren_note.strip("()"))
        else:
            notes.append(seg)
            flags.append(f"unrecognized speed segment {seg!r} (full: {raw!r})")
    return ground, fly, climb, "; ".join(notes), flags


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
