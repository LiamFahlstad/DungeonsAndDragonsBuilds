"""Logging mixin for CombatAppQt: reading and writing the encounter log and
the party's player log, appending events, Undo, and the log windows. What a
log saves of the fight, a log's combatants taken back into it, a continued
fight's turn order and the party's replay are Combat/Fight/log.py."""

from pathlib import Path

from PyQt6.QtWidgets import QDialog, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

import Combat.PartyAllies as PartyAllies
import Combat.PlayerLog as PlayerLog
from Combat.Definitions import Phase
from Combat.Arena.arena import ArenaSettings
from Combat.EncounterLogs import (
    PUBLIC_KEY,
    LogJSONEncoder,
    encounter_ally_names,
    event_text,
    read_log_status,
    write_log,
)
from Combat.LogFiles import read_json, write_json
from Combat.PlayerCombatant import combatant_from_character
from Combat.PlayerLog import has_round_events, session_label
from Combat.Effects.modifiers import hit_point_maximum

from Combat.Fight.log import (
    apply_replay_action,
    continue_fight,
    record_fight,
    replay_player_log,
    saved_map,
    slots_by_level,
    take_combatants_from,
)
from Combat.Fight.player_knowledge import may_read_log_line
from Combat.Fight.public_log import public_log_rounds
from Combat.Fight.stats import (
    _default_stats,
    compute_player_log_stats,
    long_rest_archive_sessions,
)
from .state import CombatWindowState


class LoggingMixin(CombatWindowState):
    """Mixin for logging-related methods."""

    def _write_log(self, data: dict):
        """Save `data` (the encounter log read with _read_log, plus changes)
        with the fight as it is now (record_fight)."""
        if self.log_file is None:
            return
        record_fight(self.fight, data)
        write_log(self.log_file, data)
        # The party's journal gets this log's entry once something happens in it.
        session = self._player_log_session
        if (
            session is not None
            and has_round_events(data)
            and not any(s is session for s in self.player_log_data["sessions"])
        ):
            self.player_log_data["sessions"].append(session)
            self._write_player_log()

    def _save_fight_state(self):
        """Save what changed since the last line logged, like a timer set just
        after it. A log without events is still as prepared, and stays so."""
        data = self._read_log()
        if has_round_events(data):
            self._write_log(data)

    def _read_log(self) -> dict:
        """The log's contents: the encounter's, or between encounters the
        between-encounters log's, which until its first event is just its
        header (it's written then). {} when nothing is logged."""
        if self.log_file is None:
            return {}
        if not self.log_file.exists():
            if self.phase == Phase.PARTY:
                return {
                    "type": PlayerLog.BETWEEN_ENCOUNTERS,
                    "title": PlayerLog.BETWEEN_ENCOUNTERS_TITLE,
                    "players": [
                        c["name"] for c in self.characters if c.get("_is_player")
                    ],
                }
            return {}
        return read_json(self.log_file)

    def _current_turn_character(self) -> dict | None:
        if self.phase != Phase.COMBAT or not self.initiative_order:
            return None
        return self.initiative_order[self.current_turn_idx]

    def _current_turn_name(self) -> str | None:
        """Whose turn it is: the combatant, or their initiative group."""
        char = self._current_turn_character()
        if char is None:
            return None
        return char.get("initiative_group") or char["name"]

    def _find_character_by_name(self, name: str) -> dict | None:
        for char in self.characters:
            if char.get("name") == name:
                return char
        return None

    def _log_event(
        self,
        text: str,
        note_turn: bool = True,
        character: str | None = None,
        action=None,
        value=None,
        public: bool = True,
    ) -> bool:
        """Append an event to the encounter log. One that changes someone's
        state carries `character`, `action` and `value`, which is what the
        party's state is replayed from on the next run (see Combat/PlayerLog.py).
        Without an action, `value` isn't kept: {"condition": name} just says what
        the line is about, for may_read_log_line. `public` False keeps a line off
        the player link whatever it says. Between encounters it goes to the
        between-encounters log, where players read nothing. During a short rest
        the events are collected for its player-log entry instead (RestsMixin).
        Returns whether players can read the line."""
        self._clear_status()
        turn_name = self._current_turn_name() if note_turn else None
        event: dict[str, object] = {
            "text": f"[{turn_name}'s turn] {text}" if turn_name else text
        }
        if character is not None:
            event["character"] = character
        if action is not None:
            event["action"] = action
            event["value"] = value
        if self._rest_events is not None:
            self._rest_events.append(event)
            return False
        if self.log_file is None:
            # No encounter, and no tracked party to log between encounters.
            print(f"Not logged (no encounter loaded): {event['text']}")
            return False
        # Before combat, nobody has perceived anyone yet.
        readable = (
            public
            and self.phase == Phase.COMBAT
            and may_read_log_line(str(event["text"]), character, value, self.characters)
        )
        if readable:
            event[PUBLIC_KEY] = True
        data = self._read_log()
        key = f"round_{self.round_number}"
        round_log = data.setdefault(key, [])
        index = len(round_log)
        round_log.append(event)
        if self._open_undo_point is not None:
            self._open_undo_point.log_entries.append((key, index))
        self._write_log(data)
        # Not every event changes a card, and the turn column shows the log.
        self._views_timer.start()
        return readable

    def _public_log(self) -> list[dict]:
        """What players may read of this encounter's log (see public_log.py)."""
        if self.phase != Phase.COMBAT:
            return []
        return public_log_rounds(self._read_log(), self.characters)

    def _undo_last(self):
        """Take back the last operation (see undo.py): restore the combat
        state from before it and delete the lines it logged."""
        if not self.history:
            self._show_status("Nothing to undo.")
            return
        point = self.history.pop()

        data = self._read_log()
        undone = []
        for key, index in reversed(point.log_entries):
            undone.append(event_text(data[key].pop(index)))
            if not data[key]:
                del data[key]

        turn_before = (self.round_number, self.current_turn_idx)
        point.restore(self)
        if self.selected_character is not None and not any(
            self.selected_character is c for c in self.characters
        ):
            self.selected_character = None
            self.selected_label.setText("Source: None")
        self.target_characters = [
            t for t in self.target_characters if any(t is c for c in self.characters)
        ]
        self._update_target_label()
        self.round_label.setText(f"Round {self.round_number}")

        self._write_log(data)
        for event in reversed(undone):
            print(f"Undid: {event}")
        self._rebuild_cards()
        self._refresh_turn()
        self._refresh_turn_prompts()  # the buttons the undone step set off go
        if (self.round_number, self.current_turn_idx) != turn_before:
            self._on_turn_changed()
            self.attack_roll_input.setText(point.attack_roll_text)

    def _load_log_from_path(self, path: str):
        """Play the encounter log at `path`: its combatants join the players
        already in the window, on the initiative screen for a fight that
        hasn't started, or straight into combat to continue one."""
        data = read_json(path)
        take_combatants_from(self.fight, data)
        # A log prepared before encounter allies were marked: they're on the
        # party's side all the same (the arena plan's R9).
        scenario = next(
            (s for s in self._scenarios if s.name == data.get("encounter")), None
        )
        if scenario is not None:
            PartyAllies.mark_encounter_allies(
                self.characters, encounter_ally_names(scenario)
            )
        self.round_number = data.get("round_number", 1)
        # A fight keeps its own map from when it started; one that hasn't
        # started yet plays on the encounter's painted map (map_painter.py),
        # if it has one.
        saved = saved_map(data)
        if saved is not None:
            self.arena_settings = saved
        else:
            painted = self._encounter_map(data.get("encounter") or self._scenario_name)
            self.arena_settings = (
                painted.settings.copy() if painted is not None else ArenaSettings()
            )
        self.history = []
        self.selected_character = None
        self.target_characters = []
        self.selected_label.setText("Source: None")
        self.target_label.setText("Target: None")
        self.round_label.setText(f"Round {self.round_number}")
        self._use_log_file(Path(path))
        self.current_turn_idx = 0
        if not has_round_events(data):
            self._carry_summons_over(Path(path))
            self._carry_party_allies_over(Path(path))
            self.phase = Phase.INITIATIVE
            self.initiative_order = []
            self._switch_to_initiative()
            return
        # Continuing a fight jumps straight into COMBAT, in the turn order it
        # was saved with and on the turn it stopped at.
        continue_fight(self.fight, data)
        self._switch_to_combat()

    def _carry_party_allies_over(self, log_path: Path):
        """Bring the party's allies in the encounter log at `log_path` (one
        not started yet) to how the player log says they are now: as the
        last fight left them, healed by short rests since, or rested to full
        by a long rest (Combat/PartyAllies.py)."""
        if not self.player_log_file:
            return
        changed = PartyAllies.carry_over(
            self.characters,
            self.player_log_data["sessions"],
            self.player_log_file,
            log_path,
        )
        for char in changed:
            char["spell_slots"] = slots_by_level(char.get("spell_slots"))
            self._apply_bloodied_condition(char)

    def _init_player_log(self):
        """Load the party's player log and bring the freshly built players to
        their current state: replay the events of every encounter log it lists
        since the last long rest (see Combat/PlayerLog.py)."""
        player_log_file = self.player_log_file
        assert player_log_file is not None  # only called when there is one
        self.player_log_data = PlayerLog.load(player_log_file)
        # Entries in which nothing happened (older runs wrote one per launch).
        sessions = self.player_log_data["sessions"]
        sessions[:] = [
            s for s in sessions if PlayerLog.worth_keeping(s, player_log_file)
        ]
        self._replay_party_history()

    def _set_party(self, names: list[str] | None):
        """Bring into the window the party members called `names` (the whole
        party for None), as they are now, and nobody else from the party."""
        if not self._party_sheets:
            return
        wanted = [n for n in self._party_sheets if names is None or n in names]
        if wanted == [c["name"] for c in self.characters if c.get("_is_player")]:
            return
        others = [c for c in self.characters if not c.get("_is_player")]
        self.characters = []
        for name in wanted:
            self._add_from_character_sheet(self._party_sheets[name])
        self.characters += others
        if self.player_log_file:
            self._replay_party_history()

    def _replay_party_history(self):
        assert self.player_log_file is not None
        recent = PlayerLog.since_long_rest(self.player_log_data["sessions"])
        sessions = PlayerLog.with_events(recent, self.player_log_file)
        replay_player_log(self.characters, sessions)

    def _use_log_file(self, path: Path | None):
        """Log to the encounter log at `path` from now on (None: nothing is
        logged; see _use_between_encounters_log), under its entry in the party's
        journal: the existing one when the party has been in this fight before
        (continued), else a new one, which is only written once something
        happens in the log (see _write_log)."""
        self.log_file = path
        self._player_log_session = None
        if path is None or not self.player_log_file:
            return
        ref = PlayerLog.log_ref(self.player_log_file, path)
        sessions = self.player_log_data["sessions"]
        self._player_log_session = next(
            (s for s in sessions if s.get("log") == ref),
            {
                "type": PlayerLog.ENCOUNTER,
                "scenario": self._scenario_name,
                "log": ref,
                "started_at": PlayerLog.now(),
            },
        )

    def _use_between_encounters_log(self) -> dict | None:
        """Log to the party's between-encounters log from now on: the one the
        player log ends with, which continues (its contents are returned), or
        else a new one (None is returned). A new one, like an encounter's
        entry, is only written, and added to the player log, once something
        happens in it (see _write_log). Without a tracked party nothing is
        logged between encounters."""
        self.log_file = None
        self._player_log_session = None
        if not self.player_log_file:
            return None
        session = PlayerLog.current_between_encounters(self.player_log_data["sessions"])
        if session is not None and session.get("log"):
            path = PlayerLog.resolve_log(self.player_log_file, session["log"])
            if path.exists():
                self.log_file = path
                self._player_log_session = session
                return read_json(path)
        started_at = PlayerLog.now()
        path = PlayerLog.between_encounters_log_path(self._combat_log_dir, started_at)
        self.log_file = path
        self._player_log_session = {
            "type": PlayerLog.BETWEEN_ENCOUNTERS,
            "log": PlayerLog.log_ref(self.player_log_file, path),
            "started_at": started_at,
        }
        return None

    def _rebuild_players_from_log(self):
        """Reset every player to their character sheet and replay the party's
        history onto them again, e.g. after a restart took a fight out of it.
        Each player's dict is refilled in place, so widgets keyed by it hold."""
        for char in self.characters:
            if char.get("_is_player"):
                fresh = combatant_from_character(char["_stat_block"])
                fresh["stats"] = _default_stats()
                char.clear()
                char.update(fresh)
        self._replay_party_history()

    def _apply_replay_action(self, char: dict, action: str, value):
        apply_replay_action(char, action, value)

    def _compute_player_log_stats(self) -> dict[str, dict]:
        """Aggregate lifetime stats per character name: the sessions archived
        by long rests, then every encounter in the player log."""
        if not self.player_log_file:
            return {}
        sessions = PlayerLog.with_events(
            self.player_log_data["sessions"], self.player_log_file
        )
        return compute_player_log_stats(
            {"sessions": long_rest_archive_sessions(self.player_log_file) + sessions}
        )

    def _write_player_log(self):
        if not self.player_log_file:
            return
        write_json(self.player_log_file, self.player_log_data, LogJSONEncoder)

    def _log_status_text(self) -> str:
        """One-line summary of whether player-log tracking is active, shown in the side panel."""
        if not self.player_log_file:
            return "Player log: inactive — run with --player-log to track the party across sessions."
        where = (
            session_label(self._player_log_session)
            if self._player_log_session is not None
            else "between encounters"
        )
        return f"Tracking players in {self.player_log_file.name} — {where}"

    def _show_current_log(self):
        """Display the round-by-round event history of the active encounter
        log, or between encounters what has happened since the last
        encounter or rest."""
        between = self.phase == Phase.PARTY
        if self.log_file is None or (not between and not self.log_file.exists()):
            QMessageBox.information(
                self._window,
                "Encounter Log",
                "No encounter loaded. Load one (Ctrl+O) to see its log.",
            )
            return
        data = self._read_log()
        round_keys = sorted(
            (
                k
                for k in data
                if k.startswith("round_") and k.split("_", 1)[1].isdigit()
            ),
            key=lambda k: int(k.split("_", 1)[1]),
        )

        dlg = QDialog(self._window)
        heading = "Between Encounters" if between else "Encounter Log"
        dlg.setWindowTitle(f"{heading} — {self.log_file.name}")
        dlg.setMinimumSize(480, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        text = QTextEdit()
        text.setReadOnly(True)
        if not round_keys:
            text.setPlainText("No events logged yet.")
        else:
            lines = []
            for key in round_keys:
                round_num = key.split("_", 1)[1]
                # Between encounters there are no rounds.
                if not between:
                    lines.append(f"Round {round_num}")
                for event in data[key]:
                    lines.append(f"  • {event_text(event)}")
                lines.append("")
            text.setPlainText("\n".join(lines).rstrip())
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.exec()

    def _show_player_log(self):
        """Display every session (encounter/adventure) recorded in the active player log."""
        if not self.player_log_file:
            QMessageBox.information(
                self._window,
                "Player Log",
                "No player log active — run with --player-log to enable.",
            )
            return

        dlg = QDialog(self._window)
        dlg.setWindowTitle(f"Player Log — {self.player_log_file.name}")
        dlg.setMinimumSize(480, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        text = QTextEdit()
        text.setReadOnly(True)
        lines = []

        players = [c for c in self.characters if c.get("_is_player")]
        if players:
            lines.append("Current Party")
            for c in players:
                conditions = ", ".join(c.get("conditions", [])) or "—"
                lines.append(
                    f"  {c['name']}: {c['hp']}/{hit_point_maximum(c) if 'max_hp' in c else c['hp']} HP"
                    f" (+{c.get('temp_hp', 0)} temp) — {conditions}"
                )
            lines.append("")

        # Where the party has been, newest first. The details of each fight
        # are in its encounter log.
        sessions = self.player_log_data.get("sessions", [])
        if sessions:
            lines.append("Where the party has been (newest first)")
        current_since = len(sessions) - len(PlayerLog.since_long_rest(sessions))
        for i, session in reversed(list(enumerate(sessions))):
            line = f"  {session.get('started_at', '')[:16].replace('T', ' ')}  "
            line += session_label(session)
            between = session.get("type") == PlayerLog.BETWEEN_ENCOUNTERS
            if "log" in session and not between:
                status = read_log_status(
                    PlayerLog.resolve_log(self.player_log_file, session["log"])
                )
                if status is not None:
                    where = "ended in round" if status.ended else "round"
                    line += f" — {where} {status.round_number}, "
                    line += f"{status.standing} of {status.total} standing"
            if i < current_since:
                line += "  (before the last long rest)"
            lines.append(line)
        text.setPlainText(
            "\n".join(lines).rstrip() if lines else "No player log data yet."
        )
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.exec()
