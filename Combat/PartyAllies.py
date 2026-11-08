"""The party's allies (PartySpec.allies in a campaign's encounters.py): NPCs
and creatures who travel with the party, tracked from fight to fight like the
players are. Nothing here imports Qt.

A party ally joins every encounter its party does, unless the encounter's
`players` leaves it out. Its encounter log is set up with it at full Hit
Points and marked PARTY_ALLY_KEY (EncounterLogs.prepared_log); when the
encounter is opened, the player log brings it to how it is now (carry_over):

- the last encounter log since the last long rest that has it says how it
  left that fight: its Hit Points, conditions (not ones ending on a timer or
  a save, which are fight state), death saves, spell slots and Legendary
  Resistances left;
- a short rest after that heals it by what the short rest's line in the
  player log says it healed;
- a long rest brings it back to full, as it does the players.

Like a player, it makes Death Saving Throws at 0 Hit Points instead of dying
(`death_saves`), so one that went down can be healed: it joins the next fight
as it was left. Players are replayed from events, but an ally's state is
read from the logs' combatants: the log keeps them current."""

from pathlib import Path

import Combat.PlayerLog as PlayerLog
from Combat.Definitions import Action
from Combat.LogFiles import read_json
from Core.Definitions import Condition

# Marks a party ally in an encounter log's combatants.
PARTY_ALLY_KEY = "party_ally"
# What carries from one fight to the next until a long rest.
CARRIED_KEYS = (
    "hp",
    "temp_hp",
    "conditions",
    "death_saves_fail",
    "death_saves_success",
    "spell_slots",
    "legendary_resistances_left",
)


def mark(char: dict) -> dict:
    """char (a combatant's dict) as a party ally: tracked between fights,
    and making death saves at 0 Hit Points like a player."""
    char[PARTY_ALLY_KEY] = True
    char["death_saves"] = True
    return char


def is_party_ally(char: dict) -> bool:
    return bool(char.get(PARTY_ALLY_KEY))


def _left_fight_as(char: dict) -> dict:
    """What of char, as an encounter log's combatants left it, carries into
    the next fight, with its "max_hp" to cap healing at."""
    state = {key: char[key] for key in CARRIED_KEYS if key in char}
    ending = {e.get("name") for e in char.get("timed_conditions", [])}
    for entry in char.get("repeat_saves", []):
        ending |= {entry.get("condition"), *entry.get("also", ())}
    if "conditions" in state:
        state["conditions"] = [c for c in state["conditions"] if c not in ending]
    state["max_hp"] = char.get("max_hp", char.get("hp", 0))
    return state


def _heal(state: dict, amount: int):
    """state healed by `amount`, as a short rest's heal: back up from 0 Hit
    Points, it's no longer Unconscious, and its death saves start over."""
    if amount <= 0:
        return
    was_down = state.get("hp", 0) <= 0
    state["hp"] = min(state.get("hp", 0) + amount, state["max_hp"])
    if was_down and state["hp"] > 0:
        state["death_saves_fail"] = state["death_saves_success"] = 0
        unconscious = Condition.UNCONSCIOUS.value
        state["conditions"] = [
            c for c in state.get("conditions", []) if c != unconscious
        ]


def ally_state(
    name: str,
    sessions: list[dict],
    player_log_path: str | Path,
    skip_log: str | None = None,
) -> dict | None:
    """How the party ally called `name` is now, going by the player log's
    `sessions` (see the module docstring), as the CARRIED_KEYS to update
    its full-HP dict with; None when it's as its stat block says (nothing
    since the last long rest has it). `skip_log` is the "log" of the entry
    not to read: the encounter being opened."""
    state: dict | None = None
    for session in sessions:
        kind = session.get("type")
        if kind == PlayerLog.LONG_REST:
            state = None
        elif kind == PlayerLog.SHORT_REST:
            for event in session.get("events", []):
                if (
                    state is not None
                    and isinstance(event, dict)
                    and event.get("character") == name
                    and event.get("action") == Action.HEAL
                ):
                    _heal(state, int(event["value"].get("heal", 0)))
        elif session.get("log") and session["log"] != skip_log:
            path = PlayerLog.resolve_log(player_log_path, session["log"])
            if not path.exists():
                continue
            for char in read_json(path).get("combatants", []):
                if char.get("name") == name:
                    state = _left_fight_as(char)
    if state is not None:
        del state["max_hp"]
    return state


def apply_state(char: dict, state: dict | None):
    """Bring char (a party ally at full HP) to `state` (ally_state's). Its
    Hit Points stay within its maximum, as its stat block has it now."""
    if state is None:
        return
    char.update(state)
    char["hp"] = min(char["hp"], char.get("max_hp", char["hp"]))


def carry_over(
    characters: list[dict],
    sessions: list[dict],
    player_log_path: str | Path,
    log_path: str | Path,
) -> list[dict]:
    """Bring each party ally among `characters` (the dicts of the encounter
    log at `log_path`, about to be played) to how the player log says it is
    now. Returns the ones it changed."""
    ref = PlayerLog.log_ref(player_log_path, log_path)
    changed = []
    for char in characters:
        if not is_party_ally(char):
            continue
        state = ally_state(char["name"], sessions, player_log_path, skip_log=ref)
        if state is not None:
            apply_state(char, state)
            changed.append(char)
    return changed
