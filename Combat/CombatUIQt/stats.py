"""Battle statistics configuration."""

STAT_KEYS = (
    "damage_dealt",
    "damage_taken",
    "healing_done",
    "healing_received",
    "knockouts",
    "times_downed",
    "deaths",
)


def _default_stats() -> dict:
    return {key: 0 for key in STAT_KEYS}
