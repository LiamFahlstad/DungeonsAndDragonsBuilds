"""Logging mixin for CombatAppQt."""

import dataclasses
import json
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

from Combat.Definitions import Action

from .stats import STAT_KEYS, _default_stats


class _CombatJSONEncoder(json.JSONEncoder):
    """Monster stat-block fields (MonsterAbility, DamageTypeEntry, ...) are plain
    dataclasses, not natively JSON-serializable — encode them as dicts."""

    def default(self, o):
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return super().default(o)


class LoggingMixin:
    """Mixin for logging-related methods."""

    def _write_log(self, data: dict):
        data["round_number"] = self.round_number
        data["combatants"] = [
            {k: v for k, v in c.items() if not k.startswith("_")}
            for c in self.characters
            if not c.get("_is_player")
        ]
        self.log_file.write_text(json.dumps(data, indent=2, cls=_CombatJSONEncoder))
        self._write_player_log()

    def _current_turn_name(self) -> str | None:
        if self.phase != "COMBAT" or not self.initiative_order:
            return None
        return self.initiative_order[self.current_turn_idx]["name"]

    def _find_character_by_name(self, name: str) -> dict | None:
        for char in self.characters:
            if char.get("name") == name:
                return char
        return None

    def _log_event(self, text: str, note_turn: bool = True):
        data = json.loads(self.log_file.read_text())
        key = f"round_{self.round_number}"
        turn_name = self._current_turn_name() if note_turn else None
        entry = f"[{turn_name}'s turn] {text}" if turn_name else text
        data.setdefault(key, []).append(entry)
        if self.player_log_file:
            self.player_log_data["sessions"][-1].setdefault(key, []).append(entry)
        self._write_log(data)

    def _undo_last(self):
        if not self.history:
            return
        action, value = self.history[-1]
        # Damage/Heal are applied to the target; every other tracked action
        # (conditions, spell slots, death saves) is applied to the source.
        char = (
            self.target_character
            if action in (Action.DAMAGE, Action.HEAL)
            else self.selected_character
        )
        if not char:
            return
        data = json.loads(self.log_file.read_text())
        key = f"round_{self.round_number}"
        if key not in data or not data[key]:
            return

        self.history.pop()

        if action == Action.DAMAGE:
            if isinstance(value, dict):
                hp_delta = value["hp_delta"]
                temp_delta = value["temp_delta"]
                dmg = value["dmg"]
                source_name = value.get("source_name")
                knockout = value.get("knockout", False)

                char["hp"] -= hp_delta
                char["temp_hp"] -= temp_delta

                char.setdefault("stats", _default_stats())
                char["stats"]["damage_taken"] = (
                    char["stats"].get("damage_taken", 0) - dmg
                )
                if knockout:
                    char["stats"]["times_downed"] = max(
                        char["stats"].get("times_downed", 0) - 1, 0
                    )

                if source_name:
                    source = self._find_character_by_name(source_name)
                    if source is not None:
                        source.setdefault("stats", _default_stats())
                        source["stats"]["damage_dealt"] = max(
                            source["stats"].get("damage_dealt", 0) - dmg, 0
                        )
                        if knockout:
                            source["stats"]["knockouts"] = max(
                                source["stats"].get("knockouts", 0) - 1, 0
                            )
            elif isinstance(value, tuple):
                hp_delta, temp_delta = value
                char["hp"] -= hp_delta
                char["temp_hp"] -= temp_delta
            else:
                char["hp"] += value
        elif action == Action.HEAL:
            if isinstance(value, dict):
                heal = value["heal"]
                source_name = value.get("source_name")

                char["hp"] -= heal

                char.setdefault("stats", _default_stats())
                char["stats"]["healing_received"] = max(
                    char["stats"].get("healing_received", 0) - heal, 0
                )

                if source_name:
                    source = self._find_character_by_name(source_name)
                    if source is not None:
                        source.setdefault("stats", _default_stats())
                        source["stats"]["healing_done"] = max(
                            source["stats"].get("healing_done", 0) - heal, 0
                        )
            else:
                char["hp"] -= value
        elif action == Action.ADD_CONDITION:
            if value in char["conditions"]:
                char["conditions"].remove(value)
        elif action == Action.REMOVE_CONDITION:
            if value not in char["conditions"]:
                char["conditions"].append(value)
        elif action == Action.REMOVE_SPELL_SLOT:
            char["spell_slots"][value] = char["spell_slots"].get(value, 0) + 1
        elif action == Action.ADD_SPELL_SLOT:
            char["spell_slots"][value] = max(char["spell_slots"].get(value, 0) - 1, 0)
        elif action == Action.DEATH_SAVE_FAIL:
            char["death_saves_fail"] = max(char.get("death_saves_fail", 0) - 1, 0)
            if value:
                char.setdefault("stats", _default_stats())
                char["stats"]["deaths"] = max(char["stats"].get("deaths", 0) - 1, 0)
        elif action == Action.DEATH_SAVE_SUCCESS:
            char["death_saves_success"] = max(char.get("death_saves_success", 0) - 1, 0)

        if action in (Action.DAMAGE, Action.HEAL):
            self._apply_bloodied_condition(char)

        last_event = data[key].pop()
        if self.player_log_file:
            session = self.player_log_data["sessions"][-1]
            if session.get(key):
                session[key].pop()
        self._write_log(data)
        print(f"Undid action: {last_event}")
        self._rebuild_card(char)

    def _load_log_from_path(self, path: str):
        data = json.loads(Path(path).read_text())
        if "combatants" not in data:
            QMessageBox.warning(self._window, "Error", "No combatants key in log file.")
            return
        self.characters = data["combatants"]
        for char in self.characters:
            stats = char.setdefault("stats", {})
            for key in STAT_KEYS:
                stats.setdefault(key, 0)
        self.round_number = data.get("round_number", 1)
        self.history = []
        self.selected_character = None
        self.target_character = None
        self.selected_label.setText("Source: None")
        self.target_label.setText("Target: None")
        self.round_label.setText(f"Round {self.round_number}")
        self.log_file = Path(path)
        # When loading a log we jump straight into COMBAT with the loaded order
        self.phase = "COMBAT"
        self.initiative_order = list(self.characters)
        self.current_turn_idx = 0
        self._switch_to_combat()

    def _init_player_log(self):
        """Load (or create) the persistent player log, preload player state from the
        most recent session, and start a new session entry for this run."""
        self.player_log_file.parent.mkdir(parents=True, exist_ok=True)
        if self.player_log_file.exists():
            self.player_log_data = json.loads(self.player_log_file.read_text())
        else:
            self.player_log_data = {"sessions": []}

        sessions = self.player_log_data.setdefault("sessions", [])
        if sessions:
            last_state = {c["name"]: c for c in sessions[-1].get("combatants", [])}
            for char in self.characters:
                if not char.get("_is_player"):
                    continue
                prior = last_state.get(char["name"])
                if not prior:
                    continue
                for key in (
                    "hp",
                    "temp_hp",
                    "conditions",
                    "visibility_states",
                    "death_saves_fail",
                    "death_saves_success",
                    "stats",
                    "spell_slots",
                ):
                    if key in prior:
                        char[key] = prior[key]

        session_type = "encounter" if self._scenario_name else "adventure"
        sessions.append(
            {
                "type": session_type,
                "scenario": self._scenario_name,
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "round_number": self.round_number,
                "combatants": [],
            }
        )

    def _write_player_log(self):
        if not self.player_log_file:
            return
        session = self.player_log_data["sessions"][-1]
        session["round_number"] = self.round_number
        session["combatants"] = [
            {k: v for k, v in c.items() if not k.startswith("_")}
            for c in self.characters
            if c.get("_is_player")
        ]
        self.player_log_file.write_text(
            json.dumps(self.player_log_data, indent=2, cls=_CombatJSONEncoder)
        )

    def _log_status_text(self) -> str:
        """One-line summary of whether player-log tracking is active, shown in the side panel."""
        if not self.player_log_file:
            return "Player log: inactive — run with --player-log to track the party across sessions."
        session = self.player_log_data["sessions"][-1]
        label = f"Tracking players in {self.player_log_file.name} — {session['type'].capitalize()} session"
        if session.get("scenario"):
            label += f" ({session['scenario']})"
        return label

    def _show_current_log(self):
        """Display the round-by-round event history of the active encounter log."""
        if not self.log_file.exists():
            QMessageBox.information(self._window, "Encounter Log", "No log data yet.")
            return
        data = json.loads(self.log_file.read_text())
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
                    lines.append(f"  • {event}")
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

        sessions = self.player_log_data.get("sessions", [])
        for i, session in reversed(list(enumerate(sessions, start=1))):
            header = f"Session {i} — {session['type'].capitalize()}"
            if session.get("scenario"):
                header += f" ({session['scenario']})"
            header += f" — {session.get('started_at', '')}"
            lines.append(header)
            round_keys = sorted(
                (
                    k
                    for k in session
                    if k.startswith("round_") and k.split("_", 1)[1].isdigit()
                ),
                key=lambda k: int(k.split("_", 1)[1]),
            )
            for key in round_keys:
                round_num = key.split("_", 1)[1]
                lines.append(f"  Round {round_num}")
                for event in session[key]:
                    lines.append(f"    • {event}")
            lines.append("")
        text.setPlainText(
            "\n".join(lines).rstrip() if lines else "No player log data yet."
        )
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.exec()
