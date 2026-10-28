"""Logging mixin for CombatAppQt."""

import dataclasses
import json
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

import Combat.PlayerLog as PlayerLog
from Combat.Definitions import Action
from Combat.EncounterLogs import event_text, read_log_status
from Combat.PlayerCombatant import combatant_from_character
from Combat.PlayerLog import has_round_events, session_label

from .stats import (
    DICT_STAT_KEYS,
    STAT_KEYS,
    _default_stats,
    compute_player_log_stats,
    damage_dealt_key,
    damage_taken_key,
    increment_named_stat,
    long_rest_archive_sessions,
    spell_slots_used_key,
)
from .state import CombatWindowState


class _CombatJSONEncoder(json.JSONEncoder):
    """Monster stat-block fields (MonsterAbility, DamageTypeEntry, ...) are plain
    dataclasses, not natively JSON-serializable — encode them as dicts."""

    def default(self, o):
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return super().default(o)


class LoggingMixin(CombatWindowState):
    """Mixin for logging-related methods."""

    def _write_log(self, data: dict):
        data["round_number"] = self.round_number
        data["combatants"] = [
            {k: v for k, v in c.items() if not k.startswith("_")}
            for c in self.characters
            if not c.get("_is_player")
        ]
        self.log_file.write_text(json.dumps(data, indent=2, cls=_CombatJSONEncoder))
        # The party's journal gets this log's entry once something happens in it.
        session = self._player_log_session
        if (
            session is not None
            and has_round_events(data)
            and not any(s is session for s in self.player_log_data["sessions"])
        ):
            self.player_log_data["sessions"].append(session)
            self._write_player_log()

    def _read_log(self) -> dict:
        """The encounter log's contents; {} for a new log nothing was written
        to yet (see _start_unscripted_log)."""
        if not self.log_file.exists():
            return {}
        return json.loads(self.log_file.read_text())

    def _current_turn_character(self) -> dict | None:
        if self.phase != "COMBAT" or not self.initiative_order:
            return None
        return self.initiative_order[self.current_turn_idx]

    def _current_turn_name(self) -> str | None:
        char = self._current_turn_character()
        return char["name"] if char else None

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
    ):
        """Append an event to the encounter log. One that changes someone's
        state carries `character`, `action` and `value`, which is what the
        party's state is replayed from on the next run (see Combat/PlayerLog.py)."""
        data = self._read_log()
        key = f"round_{self.round_number}"
        turn_name = self._current_turn_name() if note_turn else None
        event: dict[str, object] = {
            "text": f"[{turn_name}'s turn] {text}" if turn_name else text
        }
        if character is not None:
            event["character"] = character
        if action is not None:
            event["action"] = action
            event["value"] = value
        round_log = data.setdefault(key, [])
        index = len(round_log)
        round_log.append(event)
        if self._open_undo_point is not None:
            self._open_undo_point.log_entries.append((key, index))
        self._write_log(data)

    def _undo_last(self):
        """Take back the last operation (see undo.py): restore the combat
        state from before it and delete the lines it logged."""
        if not self.history:
            return
        point = self.history.pop()

        data = self._read_log()
        undone = []
        for key, index in reversed(point.log_entries):
            undone.append(event_text(data[key].pop(index)))
            if not data[key]:
                del data[key]

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

    def _load_log_from_path(self, path: str):
        data = json.loads(Path(path).read_text())
        if "combatants" not in data:
            QMessageBox.warning(self._window, "Error", "No combatants key in log file.")
            return
        saved_combatants = data["combatants"]
        if not saved_combatants:
            # Empty starter log (e.g. a scenario's persistent log before its first
            # session) — nothing to resume. Behave exactly like a fresh run and
            # just log to this path from now on instead of a fresh timestamped one.
            self._use_log_file(Path(path))
            self._write_log({})
            return
        # Saved logs only ever contain non-player combatants (see _write_log),
        # so splice them back in alongside whatever players are already loaded
        # rather than replacing self.characters outright.
        players = [c for c in self.characters if c.get("_is_player")]
        self.characters = players + saved_combatants
        for char in self.characters:
            stats = char.setdefault("stats", {})
            for key in STAT_KEYS:
                stats.setdefault(key, 0)
            for key in DICT_STAT_KEYS:
                stats.setdefault(key, {})
        self.round_number = data.get("round_number", 1)
        self.history = []
        self.selected_character = None
        self.target_characters = []
        self.selected_label.setText("Source: None")
        self.target_label.setText("Target: None")
        self.round_label.setText(f"Round {self.round_number}")
        self._use_log_file(Path(path))
        # When loading a log we jump straight into COMBAT with the loaded order
        self.phase = "COMBAT"
        self.initiative_order = list(self.characters)
        self.current_turn_idx = 0
        self._switch_to_combat()

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

    def _replay_party_history(self):
        assert self.player_log_file is not None
        recent = PlayerLog.since_long_rest(self.player_log_data["sessions"])
        self._replay_player_log(PlayerLog.with_events(recent, self.player_log_file))

    def _use_log_file(self, path: Path, session_type: str | None = None):
        """Log to `path` from now on, under its entry in the party's journal:
        the existing one when the party has been in this log before (a fight
        continued), else a new one, which is only written once something
        happens in the log (see _write_log). `session_type` overrides the
        type that entry gets (e.g. "short_rest")."""
        self.log_file = path
        if not self.player_log_file:
            return
        session_type = session_type or self._session_type
        ref = PlayerLog.log_ref(self.player_log_file, path)
        sessions = self.player_log_data["sessions"]
        self._player_log_session = next(
            (s for s in sessions if s.get("log") == ref),
            {
                "type": session_type,
                "scenario": (
                    self._scenario_name if session_type == PlayerLog.ENCOUNTER else None
                ),
                "log": ref,
                "started_at": PlayerLog.now(),
            },
        )

    def _start_unscripted_log(self, session_type: str | None = None):
        """Log to a new, timestamped log in the campaign's CombatLogs folder,
        e.g. adventure_2026-10-29_19-00-00.json, for a run without a scenario
        or a short rest (`session_type`). The file is only created once
        something is logged in it, so a session where nothing happens leaves
        no empty log behind."""
        session_type = session_type or self._session_type
        stem = f"{session_type}_{datetime.now():%Y-%m-%d_%H-%M-%S}"
        path = self._combat_log_dir / f"{stem}.json"
        # Never the log just left, even within the same second.
        n = 2
        while path.exists() or path == getattr(self, "log_file", None):
            path = self._combat_log_dir / f"{stem}_{n}.json"
            n += 1
        self._use_log_file(path, session_type)

    @property
    def _session_type(self) -> str:
        return (
            PlayerLog.ENCOUNTER
            if self._scenario_name
            else self._unscripted_session_type
        )

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

    def _replay_player_log(self, sessions: list[dict]):
        """Reconstruct current player state from the log history. Older sessions
        (pre-dating this action-log format) stored a full character snapshot per
        session instead — apply those as a coarse state overwrite for backward
        compatibility, then replay any structured actions on top."""
        players_by_name = {c["name"]: c for c in self.characters if c.get("_is_player")}
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
                    char = players_by_name.get(entry.get("character"))
                    if char is None:
                        continue
                    self._apply_replay_action(char, entry["action"], entry["value"])

    def _apply_replay_action(self, char: dict, action: str, value):
        """Forward-apply one recorded player-log action to a character."""
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
            if value.get("source_name"):
                source = self._find_character_by_name(value["source_name"])
                if source is not None:
                    source.setdefault("stats", _default_stats())
                    source["stats"]["damage_dealt"] = (
                        source["stats"].get("damage_dealt", 0) + value["dmg"]
                    )
                    if value.get("damage_type"):
                        type_key = damage_dealt_key(value["damage_type"])
                        source["stats"][type_key] = (
                            source["stats"].get(type_key, 0) + value["dmg"]
                        )
                    if value.get("knockout"):
                        source["stats"]["knockouts"] = (
                            source["stats"].get("knockouts", 0) + 1
                        )
            self._apply_bloodied_condition(char)
        elif action == Action.HEAL:
            was_downed = self._char_death_state(char) != "alive"
            char["hp"] += value["heal"]
            char.setdefault("stats", _default_stats())
            char["stats"]["healing_received"] = (
                char["stats"].get("healing_received", 0) + value["heal"]
            )
            if was_downed and char["hp"] > 0:
                char["death_saves_fail"] = 0
                char["death_saves_success"] = 0
            if value.get("source_name"):
                source = self._find_character_by_name(value["source_name"])
                if source is not None:
                    source.setdefault("stats", _default_stats())
                    source["stats"]["healing_done"] = (
                        source["stats"].get("healing_done", 0) + value["heal"]
                    )
            self._apply_bloodied_condition(char)
        elif action == Action.ADD_CONDITION:
            # Older logs stored the condition name as a plain string.
            cond = value["condition"] if isinstance(value, dict) else value
            if cond not in char["conditions"]:
                char["conditions"].append(cond)
            char.setdefault("stats", _default_stats())
            char["stats"]["conditions_received"] = (
                char["stats"].get("conditions_received", 0) + 1
            )
            increment_named_stat(char["stats"], "conditions_received_by_name", cond)
            source_name = value.get("source_name") if isinstance(value, dict) else None
            if source_name:
                source = self._find_character_by_name(source_name)
                if source is not None:
                    source.setdefault("stats", _default_stats())
                    source["stats"]["conditions_given"] = (
                        source["stats"].get("conditions_given", 0) + 1
                    )
                    increment_named_stat(
                        source["stats"], "conditions_given_by_name", cond
                    )
        elif action == Action.REMOVE_CONDITION:
            cond = value["condition"] if isinstance(value, dict) else value
            if cond in char["conditions"]:
                char["conditions"].remove(cond)
        elif action == Action.ADD_SPELL_SLOT:
            char["spell_slots"][value] = char["spell_slots"].get(value, 0) + 1
        elif action == Action.REMOVE_SPELL_SLOT:
            char["spell_slots"][value] = max(char["spell_slots"].get(value, 0) - 1, 0)
            char.setdefault("stats", _default_stats())
            char["stats"]["spell_slots_used"] = (
                char["stats"].get("spell_slots_used", 0) + 1
            )
            level_key = spell_slots_used_key(value)
            char["stats"][level_key] = char["stats"].get(level_key, 0) + 1
        elif action == Action.CAST_SPELL:
            spell_name = value["spell_name"] if isinstance(value, dict) else value
            char.setdefault("stats", _default_stats())
            char["stats"]["spells_cast"] = char["stats"].get("spells_cast", 0) + 1
            increment_named_stat(char["stats"], "spells_cast_by_name", spell_name)
        elif action == Action.DEATH_SAVE_FAIL:
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
                source_name = value.get("source_name")
                if source_name:
                    source = self._find_character_by_name(source_name)
                    if source is not None:
                        source.setdefault("stats", _default_stats())
                        source["stats"]["temp_hp_granted"] = (
                            source["stats"].get("temp_hp_granted", 0) + amount
                        )
            else:
                char["temp_hp"] = max(char.get("temp_hp", 0), value)
        elif action == Action.REVIVE:
            char["hp"] = value["hp"]
            char["death_saves_fail"] = 0
            char["death_saves_success"] = 0
            self._apply_bloodied_condition(char)
        elif action == Action.ENABLE_FEATURE:
            feature_name = value["feature_name"] if isinstance(value, dict) else value
            char.setdefault("stats", _default_stats())
            char["stats"]["features_enabled"] = (
                char["stats"].get("features_enabled", 0) + 1
            )
            increment_named_stat(
                char["stats"], "features_enabled_by_name", feature_name
            )
            feature = {f.name: f for f in char.get("_feature_objects", [])}.get(
                feature_name
            )
            if feature is not None and feature.uses is not None:
                used = char.setdefault("feature_uses_used", {})
                used[feature_name] = used.get(feature_name, 0) + 1
        elif action == Action.REGAIN_FEATURE_CHARGE:
            used = char.setdefault("feature_uses_used", {})
            used[value] = max(used.get(value, 0) - 1, 0)

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
        self.player_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.player_log_file.write_text(
            json.dumps(self.player_log_data, indent=2, cls=_CombatJSONEncoder)
        )

    def _log_status_text(self) -> str:
        """One-line summary of whether player-log tracking is active, shown in the side panel."""
        if not self.player_log_file or self._player_log_session is None:
            return "Player log: inactive — run with --player-log to track the party across sessions."
        session = self._player_log_session
        label = (
            f"Tracking players in {self.player_log_file.name} — "
            f"{session_label(session)}"
        )
        return label

    def _show_current_log(self):
        """Display the round-by-round event history of the active encounter log."""
        if not self.log_file.exists():
            QMessageBox.information(self._window, "Encounter Log", "No log data yet.")
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
        dlg.setWindowTitle(f"Encounter Log — {self.log_file.name}")
        dlg.setMinimumSize(480, 500)
        from .styles import QSS

        dlg.setStyleSheet(QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        text = QTextEdit()
        text.setReadOnly(True)
        if not data.get("combatants"):
            text.setPlainText(
                "No encounter combatants this session — this looks like an adventure "
                "(no --scenario). Check Player Log instead for the party's history."
            )
        elif not round_keys:
            text.setPlainText("No events logged yet.")
        else:
            lines = []
            for key in round_keys:
                round_num = key.split("_", 1)[1]
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
        from .styles import QSS

        dlg.setStyleSheet(QSS)

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
                    f"  {c['name']}: {c['hp']}/{c.get('max_hp', c['hp'])} HP"
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
            if "log" in session:
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
