"""Conditions mixin for CombatAppQt."""

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from Combat.Definitions import Action, CombatStatus
from Core.Rules import SECONDS_PER_ROUND
from .stats import _default_stats, increment_named_stat
from .state import CombatWindowState
from .styles import QSS
from .undo import undoable

# Conditions that incapacitate a creature and break concentration per 2024 D&D rules
INCAPACITATING_CONDITIONS = {
    "Incapacitated",
    "Paralyzed",
    "Petrified",
    "Stunned",
    "Unconscious",
}

# The durations the Custom Condition dialog offers, as (label, duration). A
# duration is None (until removed), {"seconds": n} (counted down a round at a
# time, on the turn it was given in), or {"until": "start" | "end", "of":
# "source" | "target"} (ends at the start or end of the source's, or each
# target's, next turn). "{source}" in a label is the source's name.
CUSTOM_CONDITION_DURATIONS: list[tuple[str, dict | None]] = [
    ("Until removed", None),
    ("Until the start of {source}'s next turn", {"until": "start", "of": "source"}),
    ("Until the end of {source}'s next turn", {"until": "end", "of": "source"}),
    ("Until the start of the target's next turn", {"until": "start", "of": "target"}),
    ("Until the end of the target's next turn", {"until": "end", "of": "target"}),
    ("1 round (6 seconds)", {"seconds": SECONDS_PER_ROUND}),
    ("1 minute (10 rounds)", {"seconds": 60}),
    ("10 minutes", {"seconds": 10 * 60}),
    ("1 hour", {"seconds": 60 * 60}),
]

# The units a custom duration can be typed in, as seconds per unit.
CUSTOM_DURATION_UNITS = {"rounds": SECONDS_PER_ROUND, "minutes": 60, "seconds": 1}


class ConditionsMixin(CombatWindowState):
    """Mixin for condition and visibility management."""

    @undoable
    def _add_condition_to(self, char: dict, cond: str, source: dict | None = None):
        if cond not in char["conditions"]:
            char["conditions"].append(cond)
            char.setdefault("stats", _default_stats())
            char["stats"]["conditions_received"] = (
                char["stats"].get("conditions_received", 0) + 1
            )
            increment_named_stat(char["stats"], "conditions_received_by_name", cond)
            source_name = source["name"] if source is not None else None
            if source is not None:
                source.setdefault("stats", _default_stats())
                source["stats"]["conditions_given"] = (
                    source["stats"].get("conditions_given", 0) + 1
                )
                increment_named_stat(source["stats"], "conditions_given_by_name", cond)
            cond_value = {
                "condition": cond,
                "source_name": source_name,
                "target_name": char["name"],
            }
            source_suffix = (
                f" from {source_name}"
                if source_name and source_name != char["name"]
                else ""
            )
            self._log_event(
                f"{char['name']} gains {cond}{source_suffix}",
                character=char["name"],
                action=Action.ADD_CONDITION,
                value=cond_value,
            )
            self._rebuild_card(char)
            # Break concentration if an incapacitating condition is applied to a concentrating character
            if (
                cond in INCAPACITATING_CONDITIONS
                and cond != "Concentrating"
                and "Concentrating" in char.get("conditions", [])
            ):
                self._remove_condition_from(char, "Concentrating", source=char)

    @undoable
    def _remove_condition_from(self, char: dict, cond: str, source: dict | None = None):
        if cond in char["conditions"]:
            char["conditions"].remove(cond)
            char.get("spell_condition_descriptions", {}).pop(cond, None)
            char.get("spell_condition_colors", {}).pop(cond, None)
            char.get("feature_condition_descriptions", {}).pop(cond, None)
            char.get("feature_condition_colors", {}).pop(cond, None)
            char.get("custom_condition_descriptions", {}).pop(cond, None)
            if "timed_conditions" in char:
                char["timed_conditions"] = [
                    e for e in char["timed_conditions"] if e["name"] != cond
                ]
            source_name = source["name"] if source is not None else None
            cond_value = {
                "condition": cond,
                "source_name": source_name,
                "target_name": char["name"],
            }
            source_suffix = (
                f" from {source_name}"
                if source_name and source_name != char["name"]
                else ""
            )
            self._log_event(
                f"{char['name']} loses {cond}{source_suffix}",
                character=char["name"],
                action=Action.REMOVE_CONDITION,
                value=cond_value,
            )
            if cond == CombatStatus.CONCENTRATING.value:
                char.pop("concentration_checks", None)
                self._end_concentration_spells(char)
            self._rebuild_card(char)

    @undoable
    def _add_condition(self):
        """Add the selected condition to every target, attributed to the source
        (mirrors Damage/Heal/Temp HP's source → target model)."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return
        source = self.selected_character or self._current_turn_character()
        cond = self.condition_combo.currentText()
        for target in list(self.target_characters):
            self._add_condition_to(target, cond, source=source)

    @undoable
    def _remove_condition(self):
        if not self.target_characters:
            self._show_status("Nothing removed: right-click a card to pick a target.")
            return
        source = self.selected_character or self._current_turn_character()
        cond = self.condition_combo.currentText()
        if not any(cond in t["conditions"] for t in self.target_characters):
            self._show_status(f"Nothing removed: no target has {cond}.")
            return
        for target in list(self.target_characters):
            self._remove_condition_from(target, cond, source=source)

    @undoable
    def _add_custom_condition(
        self, cond: str, duration: dict | None = None, notes: str = ""
    ):
        """Give every target `cond`, any text (a rules condition or an effect
        like "Hexed" or "-2 AC"), attributed to the source, for `duration`
        (see CUSTOM_CONDITION_DURATIONS) and with `notes` as its tooltip.
        Giving it again replaces its duration."""
        cond = cond.strip()
        if not cond or not self.target_characters:
            return
        source = self.selected_character or self._current_turn_character()
        turn = self._current_turn_group()
        for target in list(self.target_characters):
            if notes.strip():
                target.setdefault("custom_condition_descriptions", {})[
                    cond
                ] = notes.strip()
            self._add_condition_to(target, cond, source=source)
            timers = [
                e for e in target.get("timed_conditions", []) if e["name"] != cond
            ]
            entry = _timed_condition_entry(cond, duration, source, target, turn)
            if entry is not None:
                timers.append(entry)
            target["timed_conditions"] = timers
            self._rebuild_card(target)

    def _tick_timed_conditions(
        self, ended: list[dict], started: list[dict], new_round: bool
    ):
        """Count timed conditions down as the turn passes from `ended` to
        `started` (`new_round` when that begins a round), ending each one
        whose time or turns run out."""
        ended_names = {c["name"] for c in ended}
        started_names = {c["name"] for c in started}
        in_order = {c["name"] for c in self.initiative_order}
        for char in self.characters:
            entries = char.get("timed_conditions")
            if not entries:
                continue
            for entry in list(entries):
                if "time_left" in entry:
                    # A round passes on the turn it was given in, or at the
                    # round's start if that combatant has no turn (any more).
                    ticks_on = entry.get("ticks_on")
                    if ticks_on in started_names or (
                        new_round and ticks_on not in in_order
                    ):
                        entry["time_left"] = max(
                            entry["time_left"] - SECONDS_PER_ROUND, 0
                        )
                    expired = entry["time_left"] == 0
                else:
                    boundary = ended_names if entry["until"] == "end" else started_names
                    if entry["of"] in boundary:
                        entry["turns_left"] -= 1
                    expired = entry["turns_left"] <= 0
                if expired:
                    self._log_event(
                        f"{char['name']}'s {entry['name']} expires",
                        note_turn=False,
                        character=char["name"],
                    )
                    self._remove_condition_from(char, entry["name"])
            self._rebuild_card(char)

    def _custom_condition_suggestions(self) -> list[str]:
        """What the Custom Condition dialog's name box offers: the rules
        conditions, then everything else a combatant has right now."""
        others = {
            cond
            for char in self.characters
            for cond in char.get("conditions", [])
            if cond not in self.conditions
        }
        return list(self.conditions) + sorted(others)

    def _show_custom_condition_dialog(self):
        """Give every target any condition typed in, with an optional
        duration and note (see _add_custom_condition)."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return
        source = self.selected_character or self._current_turn_character()

        dlg = QDialog(self._window)
        dlg.setWindowTitle("Custom Condition")
        dlg.setStyleSheet(QSS)
        dlg.setFixedWidth(360)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        who = f"Targets: {', '.join(c['name'] for c in self.target_characters)}"
        if source is not None:
            who += f"\nSource: {source['name']}"
        who_lbl = QLabel(who)
        who_lbl.setObjectName("secondary")
        who_lbl.setWordWrap(True)
        layout.addWidget(who_lbl)

        layout.addWidget(QLabel("Condition:"))
        name_combo = QComboBox()
        name_combo.setEditable(True)
        name_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        name_combo.addItems(self._custom_condition_suggestions())
        name_combo.setCurrentText("")
        name_edit = name_combo.lineEdit()
        assert name_edit is not None  # an editable combo box has one
        name_edit.setPlaceholderText("e.g. Hexed, Restrained by vines, -2 AC...")
        layout.addWidget(name_combo)

        layout.addWidget(QLabel("Notes (optional, shown on hover):"))
        notes_input = QLineEdit()
        layout.addWidget(notes_input)

        layout.addWidget(QLabel("Duration:"))
        duration_combo = QComboBox()
        for label, duration in CUSTOM_CONDITION_DURATIONS:
            if duration is not None and duration.get("of") == "source":
                if source is None:
                    continue
                label = label.format(source=source["name"])
            duration_combo.addItem(label, duration)
        duration_combo.addItem("Custom...", "custom")
        layout.addWidget(duration_combo)

        custom_row = QHBoxLayout()
        amount_input = QSpinBox()
        amount_input.setRange(1, 9999)
        custom_row.addWidget(amount_input)
        unit_combo = QComboBox()
        unit_combo.addItems(list(CUSTOM_DURATION_UNITS))
        custom_row.addWidget(unit_combo)
        custom_widgets = (amount_input, unit_combo)
        layout.addLayout(custom_row)

        def show_custom_row():
            for widget in custom_widgets:
                widget.setVisible(duration_combo.currentData() == "custom")

        duration_combo.currentIndexChanged.connect(show_custom_row)
        show_custom_row()

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primaryBtn")
        cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(apply_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        # Enter in a text box and the Apply button can both fire; apply once.
        applied: list[bool] = []

        def do_apply():
            if not name_combo.currentText().strip() or applied:
                return
            applied.append(True)
            duration = duration_combo.currentData()
            if duration == "custom":
                unit = CUSTOM_DURATION_UNITS[unit_combo.currentText()]
                duration = {"seconds": amount_input.value() * unit}
            self._add_custom_condition(
                name_combo.currentText(), duration, notes_input.text()
            )
            dlg.accept()

        apply_btn.clicked.connect(do_apply)
        name_edit.returnPressed.connect(do_apply)
        notes_input.returnPressed.connect(do_apply)
        cancel_btn.clicked.connect(dlg.reject)

        name_combo.setFocus()
        dlg.exec()

    @undoable
    def _shortcut_add_concentration(self):
        """Keyboard shortcut 'C': the source starts Concentrating. Self-applied —
        a caster is always the source of their own concentration."""
        if not self.selected_character:
            self._show_status("Nothing applied: left-click a card to pick a source.")
            return
        self._add_condition_to(
            self.selected_character,
            CombatStatus.CONCENTRATING.value,
            source=self.selected_character,
        )

    @undoable
    def _shortcut_remove_concentration(self):
        """Keyboard shortcut 'Ctrl+C': remove Concentrating from the source."""
        if not self.selected_character:
            self._show_status("Nothing removed: left-click a card to pick a source.")
            return
        self._remove_condition_from(
            self.selected_character,
            CombatStatus.CONCENTRATING.value,
            source=self.selected_character,
        )

    @undoable
    def _shortcut_clear_target_conditions(self):
        """Keyboard shortcut 'Ctrl+Shift+C': remove every condition from every target."""
        if not self.target_characters:
            self._show_status("Nothing removed: right-click a card to pick a target.")
            return
        for target in list(self.target_characters):
            for cond in list(target.get("conditions", [])):
                self._remove_condition_from(target, cond)

    @undoable
    def _add_action_use(self, action_type: str):
        """Log a use of Action/Bonus Action/Reaction for the source, this round.
        Tallies reset when it becomes that combatant's turn again (see _advance_turn).
        """
        if not self.selected_character:
            self._show_status("Nothing logged: left-click a card to pick a source.")
            return
        counts = self.selected_character.setdefault("action_uses", {})
        counts[action_type] = counts.get(action_type, 0) + 1
        self._log_event(
            f"{self.selected_character['name']} uses {action_type}",
            character=self.selected_character["name"],
        )
        self._refresh_selected_card()

    @undoable
    def _remove_action_use(self, action_type: str):
        """Correct a mis-logged Action/Bonus Action/Reaction use for the source."""
        if not self.selected_character:
            self._show_status("Nothing logged: left-click a card to pick a source.")
            return
        counts = self.selected_character.setdefault("action_uses", {})
        name = self.selected_character["name"]
        if counts.get(action_type, 0) <= 0:
            self._show_status(f"Nothing refunded: {name} has no {action_type} logged.")
        else:
            counts[action_type] -= 1
            self._log_event(
                f"{self.selected_character['name']} refunds {action_type}",
                character=self.selected_character["name"],
            )
            self._refresh_selected_card()

    @undoable
    def _add_visibility(self):
        if not self.selected_character:
            self._show_status("Nothing applied: left-click a card to pick a source.")
            return
        vis = self.visibility_combo.currentText()
        visibility_states = self.selected_character.get("visibility_states", [])
        if vis not in visibility_states:
            visibility_states.append(vis)
            self._log_event(
                f"{self.selected_character['name']} gains {vis}",
                character=self.selected_character["name"],
            )
            self._refresh_selected_card()

    @undoable
    def _remove_visibility(self):
        if not self.selected_character:
            self._show_status("Nothing removed: left-click a card to pick a source.")
            return
        vis = self.visibility_combo.currentText()
        visibility_states = self.selected_character.get("visibility_states", [])
        if vis in visibility_states:
            visibility_states.remove(vis)
            self._log_event(
                f"{self.selected_character['name']} loses {vis}",
                character=self.selected_character["name"],
            )
            self._refresh_selected_card()


def _timed_condition_entry(
    cond: str,
    duration: dict | None,
    source: dict | None,
    target: dict,
    turn: list[dict],
) -> dict | None:
    """The char["timed_conditions"] entry that ends `cond` on `target` after
    `duration` (see CUSTOM_CONDITION_DURATIONS), given during `turn` (whose
    turn it is: [] outside combat). None when it lasts until removed."""
    if duration is None:
        return None
    if "seconds" in duration:
        return {
            "name": cond,
            "time_left": duration["seconds"],
            "duration": duration["seconds"],
            "ticks_on": turn[0]["name"] if turn else None,
        }
    whose = source if duration["of"] == "source" else target
    if whose is None:
        return None
    until = duration["until"]
    # The end of `whose` next turn is the end of the one after this, if this
    # is their turn; the start of their next turn is always the first to come.
    taking_turn = any(c is whose for c in turn)
    return {
        "name": cond,
        "until": until,
        "of": whose["name"],
        "turns_left": 2 if until == "end" and taking_turn else 1,
        "text": f"Until the {until} of {whose['name']}'s next turn",
    }
