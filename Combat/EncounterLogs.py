"""Each scenario's persistent encounter log, Combat/Campaigns/<C>/CombatLogs/<scenario>.json:
where it lives, how far the fight in it got, and starting it over.

A log holds the non-player combatants (HP, conditions, ...), the round number,
and one "round_<n>" list of events per round played. Each event is
{"text": ..., "character": ..., "action": ..., "value": ...}; the last three
are there when the event changed someone's state (damage, a spell slot, a
condition, ...), which is what the party's state is replayed from (see
Combat/PlayerLog.py). Logs written before that hold plain text strings.

A log without any events is a fight that never got going, so there is
nothing in it to continue. A fight the GM ended (End Encounter) has ENDED_KEY,
the time it ended; continuing it takes that back out."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from Combat.PlayerLog import ENCOUNTER, has_round_events, log_ref

EMPTY_LOG = {"round_number": 1, "combatants": []}
# When the fight was ended, in an encounter log and in its player-log entry.
ENDED_KEY = "ended_at"
# In a restarted log's backup: the player-log entries the restart took out.
UNDONE_SESSIONS_KEY = "undone_player_log_entries"


def scenario_log_path(combat_log_dir: str | Path, scenario_name: str) -> Path:
    return Path(combat_log_dir) / f"{scenario_name}.json"


def event_text(event) -> str:
    """The line an event shows as; old logs store just that line."""
    return event["text"] if isinstance(event, dict) else event


@dataclass
class EncounterLogStatus:
    round_number: int
    # Combatants in the log, and how many of them are above 0 HP.
    total: int
    standing: int
    last_played: datetime
    # The GM ended the fight (End Encounter).
    ended: bool = False

    def describe(self) -> str:
        """e.g. "Round 4, 5 of 9 standing, last played 2026-10-20 21:14", or
        "Ended in round 4, ..." for a fight the GM ended."""
        if self.standing:
            standing = f"{self.standing} of {self.total} standing"
        else:
            standing = f"all {self.total} down"
        where = (
            f"Ended in round {self.round_number}"
            if self.ended
            else f"Round {self.round_number}"
        )
        return f"{where}, {standing}, last played {self.last_played:%Y-%m-%d %H:%M}"


def read_log_status(path: str | Path) -> EncounterLogStatus | None:
    """How far the fight in the log at `path` got, or None when there is
    nothing to continue: no file, no combatants, or no event logged yet."""
    path = Path(path)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    combatants = data.get("combatants") or []
    if not combatants or not has_round_events(data):
        return None
    return EncounterLogStatus(
        round_number=data.get("round_number", 1),
        total=len(combatants),
        standing=sum(1 for c in combatants if c.get("hp", 0) > 0),
        last_played=datetime.fromtimestamp(path.stat().st_mtime),
        ended=ENDED_KEY in data,
    )


def attempt_entries(
    path: str | Path, player_log_path: str | Path, sessions: list[dict]
) -> list[dict]:
    """The player-log entries for the fight in the encounter log at `path`:
    the one pointing to it, plus, from player logs that embedded their events,
    the encounter sessions of the same scenario."""
    ref = log_ref(player_log_path, path)
    scenario = Path(path).stem
    return [
        s
        for s in sessions
        if s.get("log") == ref
        or (
            "log" not in s
            and s.get("type") == ENCOUNTER
            and s.get("scenario") == scenario
        )
    ]


def restart_log(
    path: str | Path,
    player_log_data: dict | None = None,
    player_log_path: str | Path | None = None,
) -> Path | None:
    """Empty the log at `path` so the scenario starts fresh, as if the fight
    in it never happened. A fight that got going is first copied to a
    timestamped sibling, <scenario>_restarted_<timestamp>.json, which is
    returned. Its entries are taken out of `player_log_data` (in place), so
    the party is as they were before it, and kept in that copy under
    UNDONE_SESSIONS_KEY."""
    path = Path(path)
    backup = None
    if read_log_status(path) is not None:
        data = json.loads(path.read_text())
        if player_log_data is not None and player_log_path is not None:
            sessions = player_log_data["sessions"]
            undone = attempt_entries(path, player_log_path, sessions)
            sessions[:] = [s for s in sessions if not any(s is u for u in undone)]
            data[UNDONE_SESSIONS_KEY] = undone
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup = path.with_name(f"{path.stem}_restarted_{timestamp}.json")
        backup.write_text(json.dumps(data, indent=2))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(EMPTY_LOG))
    return backup
