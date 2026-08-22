"""Battle statistics configuration."""

from Combat.Definitions import DamageType

SPELL_SLOT_LEVELS = range(1, 10)

STAT_KEYS = (
    "damage_dealt",
    "damage_taken",
    "healing_done",
    "healing_received",
    "temp_hp_granted",
    "temp_hp_received",
    "conditions_given",
    "conditions_received",
    "spell_slots_used",
    "spells_cast",
    "features_enabled",
    "knockouts",
    "times_downed",
    "deaths",
) + tuple(f"damage_dealt_{dtype.name.lower()}" for dtype in DamageType) + tuple(
    f"damage_taken_{dtype.name.lower()}" for dtype in DamageType
) + tuple(f"spell_slots_used_{level}" for level in SPELL_SLOT_LEVELS)

# Per-condition and per-spell breakdowns are open-ended (spells can apply custom
# pseudo-conditions by name, and the spell list isn't a fixed enum), so they're
# tracked as name -> count dicts instead of flat STAT_KEYS entries.
DICT_STAT_KEYS = (
    "conditions_given_by_name",
    "conditions_received_by_name",
    "spells_cast_by_name",
    "features_enabled_by_name",
)


def _default_stats() -> dict:
    stats: dict = {key: 0 for key in STAT_KEYS}
    for key in DICT_STAT_KEYS:
        stats[key] = {}
    return stats


def damage_dealt_key(damage_type: str) -> str:
    """Stat key tracking damage dealt of one specific damage type (e.g. "Fire")."""
    return f"damage_dealt_{damage_type.lower()}"


def damage_taken_key(damage_type: str) -> str:
    """Stat key tracking damage taken of one specific damage type (e.g. "Fire")."""
    return f"damage_taken_{damage_type.lower()}"


def spell_slots_used_key(level: int) -> str:
    """Stat key tracking spell slots used at one specific level (1-9)."""
    return f"spell_slots_used_{level}"


def increment_named_stat(stats: dict, dict_key: str, name: str):
    """Increment stats[dict_key][name], creating the nested dict/entry as needed."""
    by_name = stats.setdefault(dict_key, {})
    by_name[name] = by_name.get(name, 0) + 1


def decrement_named_stat(stats: dict, dict_key: str, name: str):
    """Decrement stats[dict_key][name] (undo counterpart of increment_named_stat),
    never going below 0."""
    by_name = stats.setdefault(dict_key, {})
    if by_name.get(name, 0) > 0:
        by_name[name] -= 1
