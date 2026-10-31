"""Each encounter's log, Combat/Campaigns/<C>/CombatLogs/<encounter id>.json:
preparing it, how far the fight in it got, and starting it over.

Every encounter in a campaign's encounters.py (Combat/Campaigns/ENCOUNTERS.md)
gets its log from `python -m Combat.Tools.prepare_encounters`, named after its
id; nothing else writes new logs. A prepared log starts as

    {"encounter": <id>, "title": ..., "players": [<who takes part>],
     "round_number": 1, "combatants": [<monsters and allies, full HP>]}

and the combat window then adds one "round_<n>" list of events per round
played, keeping "combatants" (HP, conditions, ...) and "round_number"
current, and once combat has started ORDER_KEY (everyone's names, players
too, in turn order) and TURN_KEY (whose turn it is), which continuing the
fight starts from. Each event is {"text": ..., "character": ..., "action": ...,
"value": ...}; the last three are there when the event changed someone's
state (damage, a spell slot, a condition, ...), which is what the party's
state is replayed from (see Combat/PlayerLog.py). Logs written before that
hold plain text strings.

A log without any events is a fight that never got going, so there is
nothing in it to continue. A fight the GM ended (End Encounter) has ENDED_KEY,
the time it ended; continuing it takes that back out."""

import dataclasses
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from Combat.PlayerCombatant import combatant_from_stat_block
from Combat.PlayerLog import ENCOUNTER, has_round_events, log_ref

# When the fight was ended, in an encounter log and in its player-log entry.
ENDED_KEY = "ended_at"
# In a restarted log's backup: the player-log entries the restart took out.
UNDONE_SESSIONS_KEY = "undone_player_log_entries"
# The keys a prepared log starts with, before "round_number" and "combatants".
# The turn order, by name, and whose turn it is (the first of a group's).
ORDER_KEY = "initiative_order"
TURN_KEY = "turn"
# Players' Concentration saves still to make, by name: players aren't in
# "combatants", and replaying their log doesn't bring these back.
PLAYER_SAVES_KEY = "player_concentration_checks"
HEADER_KEYS = ("encounter", "title", "players")


class LogJSONEncoder(json.JSONEncoder):
    """Monster stat-block fields (MonsterAbility, DamageTypeEntry, ...) are plain
    dataclasses, not natively JSON-serializable — encode them as dicts."""

    def default(self, o):
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return super().default(o)


def scenario_log_path(combat_log_dir: str | Path, scenario_name: str) -> Path:
    return Path(combat_log_dir) / f"{scenario_name}.json"


def event_text(event) -> str:
    """The line an event shows as; old logs store just that line."""
    return event["text"] if isinstance(event, dict) else event


def write_log(path: str | Path, data: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, cls=LogJSONEncoder), encoding="utf-8")


def _plain(data: dict) -> dict:
    """`data` as it reads back from a file (dataclasses as dicts, ...)."""
    return json.loads(json.dumps(data, cls=LogJSONEncoder))


def prepared_log(scenario, players: list[str]) -> dict:
    """What the log of `scenario` (a CombatScenario) starts as: its header,
    round 1, and its allies and monsters at full HP. `players` are the
    character names of the party members taking part."""
    return {
        "encounter": scenario.name,
        "title": scenario.display_title,
        "players": list(players),
        "round_number": 1,
        "combatants": [
            combatant_from_stat_block(c)
            for c in scenario.build_allies() + scenario.build_combatants()
        ],
    }


def is_prepared(path: str | Path) -> bool:
    """Whether the log at `path` was prepared for its encounter (and so can be
    played)."""
    path = Path(path)
    if not path.exists():
        return False
    return "encounter" in json.loads(path.read_text(encoding="utf-8"))


def prepare_log(
    path: str | Path, scenario, players: list[str], write: bool = True
) -> str:
    """Write the prepared log of `scenario` at `path` (unless `write` is
    False), and say what happened: "prepared" (new), "updated" (not started,
    but the config changed), "unchanged", or "in progress" for a fight that
    got going, which is left as it is except for a header it didn't have yet
    ("in progress, header added"; its last-played time is kept)."""
    path = Path(path)
    fresh = _plain(prepared_log(scenario, players))
    if not path.exists():
        if write:
            write_log(path, fresh)
        return "prepared"
    data = json.loads(path.read_text(encoding="utf-8"))
    if has_round_events(data):
        missing = {k: fresh[k] for k in HEADER_KEYS if k not in data}
        if not missing:
            return "in progress"
        if write:
            times = (path.stat().st_atime, path.stat().st_mtime)
            write_log(path, {**missing, **data})
            os.utime(path, times)
        return "in progress, header added"
    if data == fresh:
        return "unchanged"
    if write:
        write_log(path, fresh)
    return "updated"


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
        elif self.total:
            standing = f"all {self.total} down"
        else:
            standing = "no monsters"
        where = (
            f"Ended in round {self.round_number}"
            if self.ended
            else f"Round {self.round_number}"
        )
        return f"{where}, {standing}, last played {self.last_played:%Y-%m-%d %H:%M}"


def read_log_status(path: str | Path | None) -> EncounterLogStatus | None:
    """How far the fight in the log at `path` got, or None when there is
    nothing to continue: no log, or no event logged yet."""
    if path is None or not Path(path).exists():
        return None
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not has_round_events(data):
        return None
    combatants = data.get("combatants") or []
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
    fresh: dict,
    player_log_data: dict | None = None,
    player_log_path: str | Path | None = None,
) -> Path | None:
    """Put the log at `path` back to `fresh` (its prepared_log) so the
    encounter starts over, as if the fight in it never happened. A fight that
    got going is first copied to a timestamped sibling,
    <encounter>_restarted_<timestamp>.json, which is returned. Its entries are
    taken out of `player_log_data` (in place), so the party is as they were
    before it, and kept in that copy under UNDONE_SESSIONS_KEY."""
    path = Path(path)
    backup = None
    if read_log_status(path) is not None:
        data = json.loads(path.read_text(encoding="utf-8"))
        if player_log_data is not None and player_log_path is not None:
            sessions = player_log_data["sessions"]
            undone = attempt_entries(path, player_log_path, sessions)
            sessions[:] = [s for s in sessions if not any(s is u for u in undone)]
            data[UNDONE_SESSIONS_KEY] = undone
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup = path.with_name(f"{path.stem}_restarted_{timestamp}.json")
        write_log(backup, data)
    write_log(path, fresh)
    return backup
