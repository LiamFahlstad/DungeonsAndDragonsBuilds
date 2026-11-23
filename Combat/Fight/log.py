"""The fight and its logs, Qt-free (Notes/combat-ui-refactor-plan.md, step
5.3, the log): what an encounter log saves of a fight, a log's combatants
taken back into one, a saved fight continued in its turn order, and the
party's state replayed from the player log's recorded actions (see
Combat/PlayerLog.py). Reading and writing the files, the party's journal
entry and appending events stay the combat window's (LoggingMixin)."""

from Combat.Arena.arena import ArenaSettings
from Combat.Definitions import Action, Phase
from Combat.EncounterLogs import (
    ARENA_KEY,
    ORDER_KEY,
    PLAYER_FIGHT_KEYS,
    PLAYER_FIGHT_STATE_KEY,
    TURN_KEY,
)
from Combat.Effects.active_effects import upgrade_old_keys
from Combat.Summons import upgrade_keys
from Combat.WildShape import assume_form, leave_form
from Model.Creatures.MonsterStatText import upgrade_stat_block_keys

from .effect_options import row_uses_most
from .fight import INITIATIVE_KEY, Fight
from .health import ALIVE, death_state, resync_bloodied
from .monster_actions import upgrade_ability_keys
from .stats import (
    DICT_STAT_KEYS,
    STAT_KEYS,
    _default_stats,
    credit_source,
    damage_taken_key,
    event_source_name,
    increment_named_stat,
    is_counted_condition,
    spell_slots_used_key,
)

# The combatant key of the slots each slot action changes.
SLOT_POOLS = {
    Action.ADD_SPELL_SLOT: "spell_slots",
    Action.REMOVE_SPELL_SLOT: "spell_slots",
    Action.ADD_PACT_SLOT: "pact_slots",
    Action.REMOVE_PACT_SLOT: "pact_slots",
}


def slots_by_level(slots: dict | None) -> dict[int, int]:
    """Spell slots with their levels as numbers, which JSON makes strings."""
    return {int(level): count for level, count in (slots or {}).items()}


# ---- An encounter log and the fight ----


def record_fight(fight: Fight, data: dict):
    """Put in `data` (an encounter log's contents) the fight as it is now:
    the round, and during combat the turn order and whose turn it is (by
    name: players aren't in "combatants", and the dicts are rebuilt when the
    fight is continued) and the map; the non-player combatants without their
    "_" keys; and what each player's fight state holds (PLAYER_FIGHT_KEYS),
    if anything."""
    data["round_number"] = fight.round_number
    if fight.phase == Phase.COMBAT and fight.initiative_order:
        data[ORDER_KEY] = [c["name"] for c in fight.initiative_order]
        data[TURN_KEY] = fight.initiative_order[fight.current_turn_idx]["name"]
        data[ARENA_KEY] = fight.arena_settings.to_dict()
    data["combatants"] = [
        {k: v for k, v in c.items() if not k.startswith("_")}
        for c in fight.characters
        if not c.get("_is_player")
    ]
    player_state = {
        c["name"]: {key: c[key] for key in PLAYER_FIGHT_KEYS if c.get(key)}
        for c in fight.characters
        if c.get("_is_player")
    }
    player_state = {name: keys for name, keys in player_state.items() if keys}
    data.pop(PLAYER_FIGHT_STATE_KEY, None)
    if player_state:
        data[PLAYER_FIGHT_STATE_KEY] = player_state


def take_combatants_from(fight: Fight, data: dict):
    """Put the combatants of the log `data` in the fight next to the
    players already in it, and give the players what the log kept of them
    (PLAYER_FIGHT_STATE_KEY) in place of any they had."""
    # Logs only ever hold non-player combatants (see record_fight), so splice
    # them in alongside the players rather than replacing the characters.
    players = [c for c in fight.characters if c.get("_is_player")]
    fight.characters = players + data.get("combatants", [])
    player_state = data.get(PLAYER_FIGHT_STATE_KEY, {})
    for char in fight.characters:
        # A continued fight knows its order, not the rolls behind it; a
        # player's roll may be from an earlier fight in this window.
        char.pop(INITIATIVE_KEY, None)
        char["spell_slots"] = slots_by_level(char.get("spell_slots"))
        if char.get("_is_player"):
            char["pact_slots"] = slots_by_level(char.get("pact_slots"))
            for key in PLAYER_FIGHT_KEYS:
                char.pop(key, None)
            # An older log's timers, notes and repeat saves, as effects.
            saved = upgrade_old_keys(dict(player_state.get(char["name"], {})))
            char.update(saved)
        else:
            # An older log's companion_of / companion_choice, and its
            # timers, badge tooltips and repeat saves, and its stat block's
            # speeds, senses and spellcasting from before they were fields,
            # and its abilities' costs, casts and combat effects.
            upgrade_keys(char)
            upgrade_old_keys(char)
            upgrade_stat_block_keys(char)
            upgrade_ability_keys(char)
        stats = char.setdefault("stats", {})
        for key in STAT_KEYS:
            stats.setdefault(key, 0)
        for key in DICT_STAT_KEYS:
            stats.setdefault(key, {})


def saved_map(data: dict) -> ArenaSettings | None:
    """The map a fight the log `data` holds was saved with, if it was."""
    if ARENA_KEY in data:
        return ArenaSettings.from_dict(data.get(ARENA_KEY))
    return None


def saved_initiative_order(characters: list[dict], data: dict) -> list[dict]:
    """`characters` in the turn order the log `data` saved. Anyone it
    doesn't name (all of them in a log from before the order was saved)
    goes last, in their current order."""
    saved = data.get(ORDER_KEY) or []
    rank = {name: i for i, name in enumerate(saved)}
    return sorted(characters, key=lambda c: rank.get(c["name"], len(saved)))


def continue_fight(fight: Fight, data: dict):
    """Continue the fight the log `data` saved: in combat, in the turn order
    it was saved with (record_fight) and on the turn it stopped at."""
    fight.phase = Phase.COMBAT
    fight.characters[:] = saved_initiative_order(fight.characters, data)
    fight.initiative_order = list(fight.characters)
    turn = data.get(TURN_KEY)
    fight.current_turn_idx = next(
        (i for i, c in enumerate(fight.initiative_order) if c["name"] == turn), 0
    )


# ---- The party's state, replayed from the player log ----


def replay_player_log(characters: list[dict], sessions: list[dict]):
    """Reconstruct the players' (among `characters`) current state from the
    log history. Older sessions (pre-dating this action-log format) stored a
    full character snapshot per session instead — apply those as a coarse
    state overwrite for backward compatibility, then replay any structured
    actions on top."""
    players_by_name = {c["name"]: c for c in characters if c.get("_is_player")}
    if not players_by_name:
        return
    mutable_keys = (
        "hp",
        "temp_hp",
        "conditions",
        "visibility_states",
        "death_saves_fail",
        "death_saves_success",
        "stats",
        "spell_slots",
    )
    for session in sessions:
        for snapshot in session.get("combatants", []):
            char = players_by_name.get(snapshot.get("name"))
            if char is None:
                continue
            for key in mutable_keys:
                if key in snapshot:
                    char[key] = snapshot[key]
            char["spell_slots"] = slots_by_level(char.get("spell_slots"))

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
                action, value = entry["action"], entry["value"]
                # What a player earns as its source (the damage they
                # dealt), whoever it's on. A monster's own stats come
                # back with it from its encounter log's "combatants".
                source = players_by_name.get(event_source_name(action, value))
                if source is not None:
                    stats = source.setdefault("stats", _default_stats())
                    credit_source(stats, action, value)
                char = players_by_name.get(entry.get("character"))
                if char is not None:
                    apply_replay_action(char, action, value)


def apply_replay_action(char: dict, action: str, value):
    """Forward-apply one recorded player-log action to the character it's
    on. What it credits its source with is replay_player_log's."""
    if action == Action.DAMAGE:
        char["hp"] += value["hp_delta"]
        char["temp_hp"] += value["temp_delta"]
        char.setdefault("stats", _default_stats())
        char["stats"]["damage_taken"] = (
            char["stats"].get("damage_taken", 0) + value["dmg"]
        )
        if value.get("damage_type"):
            taken_type_key = damage_taken_key(value["damage_type"])
            char["stats"][taken_type_key] = (
                char["stats"].get(taken_type_key, 0) + value["dmg"]
            )
        if value.get("knockout"):
            char["stats"]["times_downed"] = char["stats"].get("times_downed", 0) + 1
        resync_bloodied(char)
    elif action == Action.HEAL:
        was_downed = death_state(char) != ALIVE
        char["hp"] += value["heal"]
        char.setdefault("stats", _default_stats())
        char["stats"]["healing_received"] = (
            char["stats"].get("healing_received", 0) + value["heal"]
        )
        if was_downed and char["hp"] > 0:
            char["death_saves_fail"] = 0
            char["death_saves_success"] = 0
        resync_bloodied(char)
    elif action == Action.ADD_CONDITION:
        # Older logs stored the condition name as a plain string.
        cond = value["condition"] if isinstance(value, dict) else value
        if cond not in char["conditions"]:
            char["conditions"].append(cond)
        char.setdefault("stats", _default_stats())
        if is_counted_condition(value):
            char["stats"]["conditions_received"] = (
                char["stats"].get("conditions_received", 0) + 1
            )
            increment_named_stat(char["stats"], "conditions_received_by_name", cond)
    elif action == Action.REMOVE_CONDITION:
        cond = value["condition"] if isinstance(value, dict) else value
        if cond in char["conditions"]:
            char["conditions"].remove(cond)
    elif action in (Action.ADD_SPELL_SLOT, Action.ADD_PACT_SLOT):
        slots = char.setdefault(SLOT_POOLS[action], {})
        slots[value] = slots.get(value, 0) + 1
    elif action in (Action.REMOVE_SPELL_SLOT, Action.REMOVE_PACT_SLOT):
        slots = char.setdefault(SLOT_POOLS[action], {})
        slots[value] = max(slots.get(value, 0) - 1, 0)
        char.setdefault("stats", _default_stats())
        char["stats"]["spell_slots_used"] = char["stats"].get("spell_slots_used", 0) + 1
        level_key = spell_slots_used_key(value)
        char["stats"][level_key] = char["stats"].get(level_key, 0) + 1
    elif action == Action.CAST_SPELL:
        if value is None:
            return  # older logs marked a spell ended by another cast like this
        spell_name = value["spell_name"] if isinstance(value, dict) else value
        char.setdefault("stats", _default_stats())
        char["stats"]["spells_cast"] = char["stats"].get("spells_cast", 0) + 1
        increment_named_stat(char["stats"], "spells_cast_by_name", spell_name)
    elif action == Action.DEATH_SAVE_FAIL:
        if isinstance(value, dict):
            # Damage taken at 0 Hit Points (DamageMixin._damage_at_zero_hp).
            if value.get("ends_stable"):
                char["death_saves_fail"] = char["death_saves_success"] = 0
            fails = char.get("death_saves_fail", 0) + value.get("failures", 1)
            char["death_saves_fail"] = 3 if value.get("massive") else min(fails, 3)
        else:
            char["death_saves_fail"] = min(char.get("death_saves_fail", 0) + 1, 3)
        if char["death_saves_fail"] >= 3:
            char.setdefault("stats", _default_stats())
            char["stats"]["deaths"] = char["stats"].get("deaths", 0) + 1
    elif action == Action.DEATH_SAVE_SUCCESS:
        char["death_saves_success"] = min(char.get("death_saves_success", 0) + 1, 3)
    elif action == Action.ADD_TEMP_HP:
        if isinstance(value, dict):
            amount = value["amount"]
            # Temporary Hit Points don't stack: keep the higher amount.
            char["temp_hp"] = max(char.get("temp_hp", 0), amount)
            char.setdefault("stats", _default_stats())
            char["stats"]["temp_hp_received"] = (
                char["stats"].get("temp_hp_received", 0) + amount
            )
        else:
            char["temp_hp"] = max(char.get("temp_hp", 0), value)
    elif action == Action.LOSE_HIT_POINTS:
        char["hp"] = max(char["hp"] + value["hp_delta"], 0)
        resync_bloodied(char)
    elif action == Action.REVIVE:
        char["hp"] = value["hp"]
        char["death_saves_fail"] = 0
        char["death_saves_success"] = 0
        resync_bloodied(char)
    elif action == Action.ENABLE_FEATURE:
        feature_name = value["feature_name"] if isinstance(value, dict) else value
        char.setdefault("stats", _default_stats())
        char["stats"]["features_enabled"] = char["stats"].get("features_enabled", 0) + 1
        increment_named_stat(char["stats"], "features_enabled_by_name", feature_name)
        feature = {f.name: f for f in char.get("_feature_objects", [])}.get(
            feature_name
        )
        counted = (
            feature.uses is not None
            if feature is not None
            else row_uses_most(char, feature_name) is not None
        )
        if counted:
            # A use that spends several (Elemental Burst's 2 Focus Points).
            count = value.get("count", 1) if isinstance(value, dict) else 1
            used = char.setdefault("feature_uses_used", {})
            used[feature_name] = used.get(feature_name, 0) + count
    elif action == Action.REGAIN_FEATURE_CHARGE:
        used = char.setdefault("feature_uses_used", {})
        used[value] = max(used.get(value, 0) - 1, 0)
    elif action == Action.WILD_SHAPE:
        try:
            assume_form(char, value["form"])
        except KeyError:
            pass  # a form their character sheet no longer has
    elif action == Action.LEAVE_WILD_SHAPE:
        leave_form(char)
    elif action in (Action.SUMMON, Action.DISMISS):
        # Nothing on the owner: what paid for it is logged on its own,
        # and the next encounter's carry-over reads which summons are out
        # (Combat/Fight/summons.py's carry_summons_over).
        pass
