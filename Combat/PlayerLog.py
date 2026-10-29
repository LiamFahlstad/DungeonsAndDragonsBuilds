"""The party's player log, Combat/Campaigns/<C>/PlayerLogs/main_party.json: a
short journal of where the party has been, which together with the encounter
logs it points to gives the party's current state.

The two logs split the work:

- An encounter log (CombatLogs/<encounter id>.json, prepared from the
  campaign's encounters.json; see Combat/EncounterLogs.py) holds everything
  that happened in one fight, in detail: every event, players' included, with
  its structured action and value.
- The player log holds one entry per encounter or rest, in the order the
  party went through them:

      {"type": "encounter", "scenario": "goblin_warband_ambush",
       "log": "../CombatLogs/goblin_warband_ambush.json", "started_at": "..."}
      {"type": "short_rest", "started_at": "...", "events": [<heals, ...>]}
      {"type": "long_rest", "started_at": "..."}

  "log" is the encounter log's path relative to the player log's folder. A
  short rest has no log of its own: its few events (heals, regained feature
  uses) are kept on its line. Nothing else happens between encounters.

The party's current state (HP, conditions, spell slots, ...) is their
character sheets with the player events of every log listed since the last
long rest replayed onto them. Restarting a fight drops its entry, so the
fight no longer counts.

Older player logs embedded each session's events ("round_<n>" lists) in the
entry itself instead of pointing to a log, and had "adventure" entries with
logs of their own; those entries are still read."""

import json
import os
from datetime import datetime
from pathlib import Path

LONG_REST = "long_rest"
SHORT_REST = "short_rest"
ENCOUNTER = "encounter"


_LOWERCASE_TITLE_WORDS = {"a", "an", "and", "at", "in", "of", "on", "the", "to"}


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def scenario_title(name: str) -> str:
    """e.g. "wrath_of_durmor" -> "Wrath of Durmor"."""
    words = name.split("_")
    return " ".join(
        word if i and word in _LOWERCASE_TITLE_WORDS else word.capitalize()
        for i, word in enumerate(words)
    )


def session_label(session: dict) -> str:
    """e.g. "Encounter: Wrath of Durmor", "Long rest", "Adventure"."""
    label = session.get("type", "session").replace("_", " ").capitalize()
    if session.get("scenario"):
        label += f": {scenario_title(session['scenario'])}"
    return label


def is_round_key(key: str) -> bool:
    return key.startswith("round_") and key.split("_", 1)[1].isdigit()


def has_round_events(data: dict) -> bool:
    """True if any "round_<n>" list in an encounter log or an old embedded
    player-log session has an entry."""
    return any(is_round_key(key) and value for key, value in data.items())


def log_ref(player_log_path: str | Path, log_path: str | Path) -> str:
    """How the player log at `player_log_path` points to the encounter log
    at `log_path`: its path relative to the player log's folder."""
    rel = os.path.relpath(
        Path(log_path).resolve(), Path(player_log_path).resolve().parent
    )
    return rel.replace(os.sep, "/")


def resolve_log(player_log_path: str | Path, ref: str) -> Path:
    return (Path(player_log_path).parent / ref).resolve()


def session_rounds(session: dict, player_log_path: str | Path) -> dict[str, list]:
    """The "round_<n>" event lists of one player-log entry: read from the
    encounter log it points to, a short rest's own "events", or embedded in
    old entries. A log that isn't on this machine contributes nothing."""
    if "events" in session:
        return {"round_1": session["events"]}
    if "log" not in session:
        return {k: v for k, v in session.items() if is_round_key(k)}
    path = resolve_log(player_log_path, session["log"])
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if is_round_key(k)}


def with_events(sessions: list[dict], player_log_path: str | Path) -> list[dict]:
    """Each entry with its events filled in (see session_rounds), in the
    shape replay and statistics read: the entry's keys plus its round lists."""
    return [
        {
            **{k: v for k, v in s.items() if not is_round_key(k)},
            **session_rounds(s, player_log_path),
        }
        for s in sessions
    ]


def since_long_rest(sessions: list[dict]) -> list[dict]:
    """The entries after the last long rest: what the party's current state
    is made of."""
    last_rest = max(
        (i for i, s in enumerate(sessions) if s.get("type") == LONG_REST),
        default=-1,
    )
    return sessions[last_rest + 1 :]


def worth_keeping(session: dict, player_log_path: str | Path) -> bool:
    """False for an entry in which nothing happened: an old embedded session
    without events, or one whose encounter log exists but is empty. An entry
    whose log isn't on this machine is kept."""
    if session.get("type") == LONG_REST or "combatants" in session:
        return True
    if "log" not in session:
        return has_round_events(session) or bool(session.get("events"))
    path = resolve_log(player_log_path, session["log"])
    return not path.exists() or has_round_events(
        session_rounds(session, player_log_path)
    )


def load(player_log_path: str | Path) -> dict:
    path = Path(player_log_path)
    if not path.exists():
        return {"sessions": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("sessions", [])
    return data


def long_rest_entry() -> dict:
    """A long rest: from here on the party starts from their full character
    sheets again. Earlier entries stay for the statistics."""
    return {"type": LONG_REST, "started_at": now()}


def append_long_rest(player_log_path: str | Path):
    """Record a long rest (see long_rest_entry) in the player log file."""
    data = load(player_log_path)
    data["sessions"].append(long_rest_entry())
    path = Path(player_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
