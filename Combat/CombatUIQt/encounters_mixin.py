"""Encounter-loading mixin for CombatAppQt: open a scenario's persistent
encounter log, continuing the fight in it or restarting it, either at launch
(--scenario / --log) or from the Load Encounter dialog."""

import json
from collections import Counter
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
)

import Combat.PlayerLog as PlayerLog
from Combat.EncounterLogs import (
    ENDED_KEY,
    read_log_status,
    restart_log,
    scenario_log_path,
)
from Combat.PlayerLog import scenario_title
from Combat.Scenario import CombatScenario

from .state import CombatWindowState
from .styles import QSS

CONTINUE = "continue"
RESTART = "restart"


def _monster_summary(combatants: list) -> str:
    counts = Counter(c.combatant_type for c in combatants)
    return ", ".join(
        f"{count}× {name}" if count > 1 else name for name, count in counts.items()
    )


class EncountersMixin(CombatWindowState):
    """Mixin for loading, continuing and restarting encounters."""

    def _ask_continue_or_restart(
        self, path: Path, title: str, can_restart: bool = True
    ) -> str | None:
        """CONTINUE or RESTART for the encounter log at `path`, asking the GM
        only when it holds a fight in progress; None if they cancelled. A log
        with nothing to continue restarts, unless there are no fresh monsters
        to restart with (`can_restart` False)."""
        status = read_log_status(path)
        if status is None:
            return RESTART if can_restart else CONTINUE
        box = QMessageBox(self._window)
        box.setIcon(QMessageBox.Icon.Question)
        if status.ended:
            box.setWindowTitle("Encounter Ended")
            box.setText(f"{title} was ended. Continuing it reopens the fight.")
        else:
            box.setWindowTitle("Encounter in Progress")
            box.setText(f"{title} has a fight in progress.")
        info = status.describe()
        if can_restart:
            info += (
                "\n\nRestarting undoes the whole fight: the monsters come back "
                "fresh and the party is as they were before it. The old logs "
                "are kept as a backup next to it."
            )
        box.setInformativeText(info)
        continue_btn = box.addButton(
            "Continue Encounter", QMessageBox.ButtonRole.AcceptRole
        )
        restart_btn = (
            box.addButton("Restart Encounter", QMessageBox.ButtonRole.DestructiveRole)
            if can_restart
            else None
        )
        box.addButton(QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(continue_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked is continue_btn:
            return CONTINUE
        if restart_btn is not None and clicked is restart_btn:
            return RESTART
        return None

    def _open_encounter_log(self, path: Path, restart: bool):
        """Log to `path` from now on: resume the fight saved in it, or empty it
        first (keeping a backup) so the monsters already loaded start fresh.
        A restart also takes that fight out of the player log, and the party
        goes back to how they were before it. Continuing a fight the GM ended
        reopens it."""
        if restart or not path.exists():
            session_count = len(self.player_log_data["sessions"])
            backup = restart_log(path, self.player_log_data, self.player_log_file)
            if backup is not None:
                print(f"Restarted {path.name}; the old log is backed up to: {backup}")
            if len(self.player_log_data["sessions"]) != session_count:
                self._write_player_log()
                self._rebuild_players_from_log()
        self._load_log_from_path(str(path))
        if ENDED_KEY in json.loads(path.read_text()):
            self._mark_encounter_ended(None)
        self._refresh_encounter_labels()

    def _refresh_encounter_labels(self):
        title = "DnD Combat Engine"
        if self._scenario_name:
            title += f" — {scenario_title(self._scenario_name)}"
        self._window.setWindowTitle(title)
        self._log_status_label.setText(self._log_status_text())
        self._end_encounter_btn.setEnabled(self._scenario_name is not None)
        self._refresh_rest_buttons()

    def _reset_encounter_state(self):
        """Back to the initiative screen for whoever is in self.characters,
        with nothing selected, round 1 and nothing to undo."""
        self.round_number = 1
        self.round_label.setText("Round 1")
        self.history = []
        self.phase = "INITIATIVE"
        self.initiative_order = []
        self.current_turn_idx = 0
        self.selected_character = None
        self.target_characters = []
        self.selected_label.setText("Source: None")
        self._update_target_label()
        self._switch_to_initiative()

    def _load_encounter(self, scenario: CombatScenario, restart: bool):
        """Swap the monsters in the window for `scenario`'s, keeping the party
        as it is, and continue or restart that scenario's encounter log. The
        encounter being left needs no saving: its log is written on every event."""
        self.characters = [c for c in self.characters if c.get("_is_player")]
        for combatant in scenario.build_allies() + scenario.build_combatants():
            self._add_basic_combatant(combatant)
        self.combatants_per_column = scenario.combatants_per_column
        self._scenario_name = scenario.name
        self._reset_encounter_state()
        self._open_encounter_log(
            scenario_log_path(self._combat_log_dir, scenario.name), restart
        )

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
        and the player log), the monsters leave the window, and the party
        carries on as they are in a new adventure session."""
        if self._scenario_name is None:
            return
        title = scenario_title(self._scenario_name)
        answer = QMessageBox.question(
            self._window,
            "End Encounter",
            f"End {title}?\n\nThe fight is saved as ended and the party carries "
            "on in an adventure session. Load Encounter can reopen it later.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if read_log_status(self.log_file) is not None:
            self._log_event(f"--- {title} ended ---", note_turn=False)
            self._mark_encounter_ended(PlayerLog.now())

        self.characters = [c for c in self.characters if c.get("_is_player")]
        self._scenario_name = None
        self._reset_encounter_state()
        self._start_unscripted_log()
        self._refresh_encounter_labels()

    def _show_load_encounter_dialog(self):
        """Pick one of the campaign's scenarios, see how far its fight got,
        and continue or (re)start it."""
        if not self._scenarios:
            QMessageBox.information(
                self._window,
                "Load Encounter",
                "This campaign has no scenarios to load.",
            )
            return

        dlg = QDialog(self._window)
        dlg.setWindowTitle("Load Encounter")
        dlg.setMinimumSize(560, 460)
        dlg.setStyleSheet(QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        info = QLabel(
            "Pick a scenario. A fight in progress can be continued where it "
            "stopped, or restarted as if it never happened: fresh monsters, and "
            "the party as they were before it (the old logs are kept as a "
            "backup)."
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
        statuses = {}
        for scenario in self._scenarios:
            status = read_log_status(
                scenario_log_path(self._combat_log_dir, scenario.name)
            )
            statuses[scenario.name] = status
            heading = scenario_title(scenario.name)
            if scenario.name == self._scenario_name:
                heading += "  (current)"
            detail = status.describe() if status else "Not started"
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
        restart_btn = QPushButton("Start Encounter")
        btn_row.addWidget(restart_btn)
        continue_btn = QPushButton("Continue Encounter")
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
            in_progress = statuses[scenario.name] is not None
            text = f"Monsters: {_monster_summary(scenario.build_combatants())}"
            allies = scenario.build_allies()
            if allies:
                text += f"\nAllies: {_monster_summary(allies)}"
            details.setText(text)
            restart_btn.setEnabled(True)
            restart_btn.setText(
                "Restart Encounter" if in_progress else "Start Encounter"
            )
            continue_btn.setEnabled(in_progress)

        choice: list[str] = []
        restart_btn.clicked.connect(lambda: (choice.append(RESTART), dlg.accept()))
        continue_btn.clicked.connect(lambda: (choice.append(CONTINUE), dlg.accept()))
        scenario_list.currentItemChanged.connect(lambda *_: on_selection_changed())
        scenario_list.itemDoubleClicked.connect(
            lambda _item: (
                continue_btn if continue_btn.isEnabled() else restart_btn
            ).click()
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
