"""Battle statistics configuration."""

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
)


def _default_stats() -> dict:
    return {key: 0 for key in STAT_KEYS}
