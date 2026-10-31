"""Encounter mixin for CombatAppQt: play the campaign's encounters from their
prepared logs (Combat/EncounterLogs.py), at launch (--scenario) or from the
Load Encounter dialog, continuing a fight in progress or restarting it; end
one; and the party view shown between encounters, where nothing is logged."""

import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import Combat.PlayerLog as PlayerLog
from Combat.EncounterConfig import resolve_players
from Combat.EncounterLogs import (
    ENDED_KEY,
    is_prepared,
    prepared_log,
    read_log_status,
    restart_log,
    scenario_log_path,
)
from Combat.Scenario import CombatScenario

from .state import CombatWindowState
from .styles import QSS

CONTINUE = "continue"
RESTART = "restart"
PREPARE_HINT = (
    "Its log isn't prepared yet: run `python -m Combat.Tools.prepare_encounters` "
    "after adding it to the campaign's encounters.py."
)


class EncountersMixin(CombatWindowState):
    """Mixin for loading, continuing, restarting and ending encounters."""

    def _scenario(self, name: str | None) -> CombatScenario | None:
        return next((s for s in self._scenarios if s.name == name), None)

    def _scenario_title(self, name: str) -> str:
        scenario = self._scenario(name)
        return scenario.display_title if scenario else PlayerLog.scenario_title(name)

    def _ask_continue_or_restart(self, path: Path, title: str) -> str | None:
        """CONTINUE or RESTART for the encounter log at `path`, asking the GM
        only when it holds a fight in progress (or one that was ended); None
        if they cancelled. A prepared log nothing happened in just opens."""
        status = read_log_status(path)
        if status is None:
            return CONTINUE
        box = QMessageBox(self._window)
        box.setIcon(QMessageBox.Icon.Question)
        if status.ended:
            box.setWindowTitle("Encounter Ended")
            box.setText(f"{title} was ended. Continuing it reopens the fight.")
        else:
            box.setWindowTitle("Encounter in Progress")
            box.setText(f"{title} has a fight in progress.")
        box.setInformativeText(
            status.describe()
            + "\n\nRestarting undoes the whole fight: the monsters come back "
            "fresh and the party is as they were before it. The old log is "
            "kept as a backup next to it."
        )
        continue_btn = box.addButton(
            "Continue Encounter", QMessageBox.ButtonRole.AcceptRole
        )
        restart_btn = box.addButton(
            "Restart Encounter", QMessageBox.ButtonRole.DestructiveRole
        )
        box.addButton(QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(continue_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked is continue_btn:
            return CONTINUE
        if clicked is restart_btn:
            return RESTART
        return None

    def _open_scenario_at_start(self, path: Path) -> bool:
        """Open the --scenario encounter's log when the window starts; False
        if the GM cancelled."""
        assert self._scenario_name is not None
        choice = self._ask_continue_or_restart(
            path, self._scenario_title(self._scenario_name)
        )
        if choice is None:
            return False
        self._open_encounter_log(path, restart=choice == RESTART)
        return True

    def _encounter_players(self, scenario: CombatScenario, path: Path) -> list[str]:
        """Who takes part in `scenario`: from its config when the party is
        known, else as its log says."""
        if self._party_sheets:
            try:
                return resolve_players(scenario.players, list(self._party_sheets))
            except KeyError:
                pass
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")).get("players", [])
        return []

    def _open_encounter_log(self, path: Path, restart: bool):
        """Play the current scenario's prepared log at `path`: continue the
        fight saved in it, or (`restart`) put it back to its prepared state
        first, keeping a backup. A restart also takes that fight out of the
        player log, and the party goes back to how they were before it.
        Continuing a fight the GM ended reopens it. The party in the window
        becomes the players the log lists."""
        scenario = self._scenario(self._scenario_name)
        if restart and scenario is not None:
            fresh = prepared_log(scenario, self._encounter_players(scenario, path))
            session_count = len(self.player_log_data["sessions"])
            backup = restart_log(
                path,
                fresh,
                self.player_log_data if self.player_log_file else None,
                self.player_log_file,
            )
            if backup is not None:
                print(f"Restarted {path.name}; the old log is backed up to: {backup}")
            if len(self.player_log_data["sessions"]) != session_count:
                self._write_player_log()
                self._rebuild_players_from_log()
        data = json.loads(path.read_text(encoding="utf-8"))
        self._set_party(data.get("players"))
        self._load_log_from_path(str(path))
        if ENDED_KEY in data:
            self._mark_encounter_ended(None)
        self._refresh_encounter_labels()

    def _refresh_encounter_labels(self):
        title = "DnD Combat Engine"
        if self._scenario_name:
            title += f" — {self._scenario_title(self._scenario_name)}"
        self._window.setWindowTitle(title)
        self._log_status_label.setText(self._log_status_text())
        self._end_encounter_btn.setEnabled(self._scenario_name is not None)
        self._add_combatant_btn.setEnabled(self.phase != "PARTY")
        self._refresh_rest_buttons()

    def _clear_encounter_state(self):
        """Round 1, nothing selected and nothing to undo."""
        self.round_number = 1
        self.round_label.setText("Round 1")
        self.history = []
        self.initiative_order = []
        self.current_turn_idx = 0
        self.selected_character = None
        self.target_characters = []
        self.selected_label.setText("Source: None")
        self._update_target_label()

    def _load_encounter(self, scenario: CombatScenario, restart: bool):
        """Swap the encounter in the window for `scenario`, from its prepared
        log: continue it, or restart it. The encounter being left needs no
        saving: its log is written on every event."""
        path = scenario_log_path(self._combat_log_dir, scenario.name)
        if not is_prepared(path):
            QMessageBox.warning(
                self._window,
                "Load Encounter",
                f"{scenario.display_title}: {PREPARE_HINT}",
            )
            return
        self.characters = [c for c in self.characters if c.get("_is_player")]
        self.combatants_per_column = scenario.combatants_per_column
        self._scenario_name = scenario.name
        self._clear_encounter_state()
        self._open_encounter_log(path, restart)

    def _mark_encounter_ended(self, ended_at: str | None):
        """Record in the encounter log and its player-log entry that the fight
        ended at `ended_at`, or, with None, that it is going on again."""
        data = self._read_log()
        session = self._player_log_session
        targets = [data]
        if session is not None and any(
            s is session for s in self.player_log_data["sessions"]
        ):
            targets.append(session)
        for target in targets:
            if ended_at is None:
                target.pop(ENDED_KEY, None)
            else:
                target[ENDED_KEY] = ended_at
        self._write_log(data)
        self._write_player_log()

    def _end_encounter(self):
        """End the current fight: it's recorded as ended (in its encounter log
        and the player log), and the window goes back to the party between
        encounters."""
        if self._scenario_name is None:
            return
        title = self._scenario_title(self._scenario_name)
        answer = QMessageBox.question(
            self._window,
            "End Encounter",
            f"End {title}?\n\nThe fight is saved as ended and the window goes "
            "back to the party between encounters. Load Encounter can reopen it.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if read_log_status(self.log_file) is not None:
            self._log_event(f"--- {title} ended ---", note_turn=False)
            self._mark_encounter_ended(PlayerLog.now())
        self._leave_encounter()

    def _leave_encounter(self):
        """Back to the whole party between encounters: no monsters, and
        nothing is logged until an encounter is loaded."""
        self.characters = [c for c in self.characters if c.get("_is_player")]
        self._scenario_name = None
        self._clear_encounter_state()
        self._use_log_file(None)
        self._set_party(None)
        self.phase = "PARTY"
        self._show_party_view()
        self._refresh_encounter_labels()

    # ── The party view, between encounters ───────────────────────────────

    def _show_party_view(self):
        old = self._scroll_area.takeWidget()
        if old is not None and old is not self._cards_container:
            old.deleteLater()
        self._cards_container.hide()
        self._init_tracker_container.hide()
        self._turn_divider.hide()
        self._prev_turn_btn.hide()
        self._next_turn_btn.hide()
        self._turn_panel.hide()
        self._initiative_widget = None
        self._scroll_area.setWidget(self._build_party_view())

    def _build_party_view(self) -> QWidget:
        """The party as they are now, and what can be done between encounters."""
        container = QWidget()
        container.setObjectName("initiativeContainer")
        outer = QVBoxLayout(container)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        header = QLabel("Between encounters")
        header.setStyleSheet("color: #c9a84c; font-size: 16px; font-weight: bold;")
        outer.addWidget(header)
        hint = QLabel(
            "Load an encounter (Ctrl+O) to play a fight, or rest the party. "
            "Nothing is logged between encounters."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #a0a0b0;")
        outer.addWidget(hint)
        outer.addWidget(self._make_divider())

        players = [c for c in self.characters if c.get("_is_player")]
        if not players:
            none = QLabel("No tracked party (run with --player-log to track one).")
            none.setStyleSheet("color: #a0a0b0;")
            outer.addWidget(none)
        for char in players:
            line = f"{char['name']}:  {char['hp']}/{char.get('max_hp', char['hp'])} HP"
            if char.get("temp_hp"):
                line += f"  (+{char['temp_hp']} temp)"
            slots = char.get("spell_slots") or {}
            if slots:
                line += "  ·  Slots " + " ".join(
                    f"L{level}:{left}" for level, left in sorted(slots.items())
                )
            if char.get("conditions"):
                line += "  ·  " + ", ".join(char["conditions"])
            label = QLabel(line)
            label.setStyleSheet("font-size: 13px;")
            outer.addWidget(label)
        outer.addStretch()
        return container

    # ── Load Encounter ───────────────────────────────────────────────────

    def _show_load_encounter_dialog(self):
        """Pick one of the campaign's encounters, see what it is and how far
        its fight got, and start, continue or restart it."""
        if not self._scenarios:
            QMessageBox.information(
                self._window,
                "Load Encounter",
                "This campaign's encounters.py lists no encounters.",
            )
            return

        dlg = QDialog(self._window)
        dlg.setWindowTitle("Load Encounter")
        dlg.setMinimumSize(560, 520)
        dlg.setStyleSheet(QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        info = QLabel(
            "The campaign's encounters (its encounters.py). A fight in "
            "progress can be continued where it stopped, or restarted as if it "
            "never happened: fresh monsters, and the party as they were before "
            "it (the old log is kept as a backup)."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #a0a0b0;")
        layout.addWidget(info)

        scenario_list = QListWidget()
        scenario_list.setStyleSheet(
            "QListWidget { background: #16213e; border: 1px solid #0f3460; }"
            "QListWidget::item { padding: 6px 10px; }"
            "QListWidget::item:selected { background: #1e2d5a; color: #eaeaea; }"
        )
        prepared = {}
        statuses = {}
        for scenario in self._scenarios:
            path = scenario_log_path(self._combat_log_dir, scenario.name)
            prepared[scenario.name] = is_prepared(path)
            statuses[scenario.name] = read_log_status(path)
            heading = scenario.display_title
            if scenario.name == self._scenario_name:
                heading += "  (current)"
            if not prepared[scenario.name]:
                detail = "Not prepared"
            elif statuses[scenario.name] is None:
                detail = "Ready"
            else:
                detail = statuses[scenario.name].describe()
            item = QListWidgetItem(f"{heading}\n    {detail}")
            item.setData(Qt.ItemDataRole.UserRole, scenario)
            scenario_list.addItem(item)
        layout.addWidget(scenario_list, stretch=1)

        details = QLabel()
        details.setWordWrap(True)
        layout.addWidget(details)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        restart_btn = QPushButton("Restart Encounter")
        btn_row.addWidget(restart_btn)
        continue_btn = QPushButton("Start Encounter")
        continue_btn.setDefault(True)
        btn_row.addWidget(continue_btn)
        layout.addLayout(btn_row)

        def selected() -> CombatScenario | None:
            item = scenario_list.currentItem()
            return item.data(Qt.ItemDataRole.UserRole) if item else None

        def on_selection_changed():
            scenario = selected()
            if scenario is None:
                details.setText("")
                restart_btn.setEnabled(False)
                continue_btn.setEnabled(False)
                return
            lines = []
            if scenario.description:
                lines.append(scenario.description)
            if scenario.difficulty:
                lines.append(f"Difficulty: {scenario.difficulty}")
            players = (
                ", ".join(scenario.players) if scenario.players else "the whole party"
            )
            lines.append(f"Players: {players}")
            lines.append(f"Monsters: {', '.join(scenario.monster_summary) or 'none'}")
            if scenario.ally_summary:
                lines.append(f"Allies: {', '.join(scenario.ally_summary)}")
            if not prepared[scenario.name]:
                lines.append(PREPARE_HINT)
            details.setText("\n".join(lines))
            in_progress = statuses[scenario.name] is not None
            continue_btn.setEnabled(prepared[scenario.name])
            continue_btn.setText(
                "Continue Encounter" if in_progress else "Start Encounter"
            )
            restart_btn.setEnabled(in_progress)

        choice: list[str] = []
        restart_btn.clicked.connect(lambda: (choice.append(RESTART), dlg.accept()))
        continue_btn.clicked.connect(lambda: (choice.append(CONTINUE), dlg.accept()))
        scenario_list.currentItemChanged.connect(lambda *_: on_selection_changed())
        scenario_list.itemDoubleClicked.connect(
            lambda _item: continue_btn.click() if continue_btn.isEnabled() else None
        )

        current = next(
            (i for i, s in enumerate(self._scenarios) if s.name == self._scenario_name),
            0,
        )
        scenario_list.setCurrentRow(current)
        on_selection_changed()

        if dlg.exec() != QDialog.DialogCode.Accepted or not choice:
            return
        scenario = selected()
        if scenario is not None:
            self._load_encounter(scenario, restart=choice[0] == RESTART)
