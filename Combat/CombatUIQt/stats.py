"""Battle statistics configuration."""

from Combat.Definitions import Action, DamageType

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


def compute_player_log_stats(player_log_data: dict) -> dict[str, dict]:
    """Aggregate lifetime stats per character name from every session in a
    player log dict (as loaded from a Combat/PlayerLogs/*.json file). Mirrors
    the forward-apply logic in logging_mixin.py's _apply_replay_action, but
    accumulates into plain stat dicts instead of mutating character objects."""
    stats_by_name: dict[str, dict] = {}

    def stats_for(name: str) -> dict:
        return stats_by_name.setdefault(name, _default_stats())

    for session in player_log_data.get("sessions", []):
        round_keys = sorted(
            (
                k
                for k in session
                if k.startswith("round_") and k.split("_", 1)[1].isdigit()
            ),
            key=lambda k: int(k.split("_", 1)[1]),
        )
        for key in round_keys:
            for entry in session[key]:
                if not isinstance(entry, dict) or "action" not in entry:
                    continue
                action = entry["action"]
                value = entry["value"]
                character = entry.get("character")
                if action == Action.DAMAGE and character:
                    s = stats_for(character)
                    s["damage_taken"] += value["dmg"]
                    if value.get("damage_type"):
                        s[damage_taken_key(value["damage_type"])] += value["dmg"]
                    if value.get("knockout"):
                        s["times_downed"] += 1
                    source_name = value.get("source_name")
                    if source_name:
                        stats_for(source_name)["damage_dealt"] += value["dmg"]
                        if value.get("damage_type"):
                            type_key = damage_dealt_key(value["damage_type"])
                            stats_for(source_name)[type_key] += value["dmg"]
                        if value.get("knockout"):
                            stats_for(source_name)["knockouts"] += 1
                elif action == Action.HEAL and character:
                    s = stats_for(character)
                    s["healing_received"] += value["heal"]
                    source_name = value.get("source_name")
                    if source_name:
                        stats_for(source_name)["healing_done"] += value["heal"]
                elif action == Action.DEATH_SAVE_FAIL and character and value:
                    stats_for(character)["deaths"] += 1
                elif action == Action.ADD_TEMP_HP and character:
                    amount = value["amount"] if isinstance(value, dict) else value
                    stats_for(character)["temp_hp_received"] += amount
                    source_name = value.get("source_name") if isinstance(value, dict) else None
                    if source_name:
                        stats_for(source_name)["temp_hp_granted"] += amount
                elif action == Action.ADD_CONDITION and character:
                    cond = value["condition"] if isinstance(value, dict) else value
                    target_stats = stats_for(character)
                    target_stats["conditions_received"] += 1
                    increment_named_stat(
                        target_stats, "conditions_received_by_name", cond
                    )
                    source_name = value.get("source_name") if isinstance(value, dict) else None
                    if source_name:
                        source_stats = stats_for(source_name)
                        source_stats["conditions_given"] += 1
                        increment_named_stat(
                            source_stats, "conditions_given_by_name", cond
                        )
                elif action == Action.REMOVE_SPELL_SLOT and character:
                    s = stats_for(character)
                    s["spell_slots_used"] += 1
                    level = value if isinstance(value, int) else None
                    if level is not None:
                        s[spell_slots_used_key(level)] += 1
                elif action == Action.CAST_SPELL and character:
                    spell_name = value["spell_name"] if isinstance(value, dict) else value
                    s = stats_for(character)
                    s["spells_cast"] += 1
                    increment_named_stat(s, "spells_cast_by_name", spell_name)
    return stats_by_name
