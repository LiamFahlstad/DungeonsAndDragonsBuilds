"""Battle statistics configuration."""

from Combat.Definitions import DamageType

STAT_KEYS = (
    "damage_dealt",
    "damage_taken",
    "healing_done",
    "healing_received",
    "temp_hp_granted",
    "temp_hp_received",
    "conditions_applied",
    "spell_slots_used",
    "knockouts",
    "times_downed",
    "deaths",
) + tuple(f"damage_dealt_{dtype.name.lower()}" for dtype in DamageType)


def _default_stats() -> dict:
    return {key: 0 for key in STAT_KEYS}


def damage_dealt_key(damage_type: str) -> str:
    """Stat key tracking damage dealt of one specific damage type (e.g. "Fire")."""
    return f"damage_dealt_{damage_type.lower()}"
