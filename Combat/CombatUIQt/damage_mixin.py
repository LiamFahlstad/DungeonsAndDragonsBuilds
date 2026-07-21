"""Damage/healing mixin for CombatAppQt."""

import random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from Combat.Definitions import Action
from .stats import _default_stats
from .styles import QSS


class DamageMixin:
    """Mixin for damage and healing related methods."""

    def _apply_bloodied_condition(self, char: dict):
        """Auto-apply/remove Bloodied condition based on HP threshold."""
        max_hp = char.get("max_hp", 1)
        hp = char.get("hp", 0)
        is_bloodied = "Bloodied" in char.get("conditions", [])
        should_be_bloodied = hp > 0 and hp <= max_hp / 2

        if should_be_bloodied and not is_bloodied:
            char["conditions"].append("Bloodied")
        elif not should_be_bloodied and is_bloodied:
            char["conditions"].remove("Bloodied")

    def _apply_damage(self):
        if not self.target_character:
            return
        try:
            dmg = int(self.damage_input.text())
        except ValueError:
            return

        target = self.target_character

        source = self.selected_character
        source_name = source["name"] if source is not None else None

        pre_hp = target["hp"]
        pre_temp = target["temp_hp"]

        temp_reduction = min(target["temp_hp"], dmg)
        target["temp_hp"] -= temp_reduction
        target["hp"] -= dmg - temp_reduction

        hp_delta = target["hp"] - pre_hp
        temp_delta = target["temp_hp"] - pre_temp

        knockout = pre_hp > 0 and target["hp"] <= 0

        target.setdefault("stats", _default_stats())
        target["stats"]["damage_taken"] = target["stats"].get("damage_taken", 0) + dmg
        if knockout:
            target["stats"]["times_downed"] = target["stats"].get("times_downed", 0) + 1

        if source is not None:
            source.setdefault("stats", _default_stats())
            source["stats"]["damage_dealt"] = source["stats"].get("damage_dealt", 0) + dmg
            if knockout:
                source["stats"]["knockouts"] = source["stats"].get("knockouts", 0) + 1

        self.history.append(
            (
                Action.DAMAGE,
                {
                    "hp_delta": hp_delta,
                    "temp_delta": temp_delta,
                    "dmg": dmg,
                    "source_name": source_name,
                    "knockout": knockout,
                },
            )
        )
        source_suffix = f" from {source_name}" if source_name else ""
        self._log_event(f"{target['name']} takes {dmg} damage{source_suffix}")

        # Auto-apply bloodied condition
        self._apply_bloodied_condition(target)

        self._rebuild_card(target)

        if "Concentrating" in target.get("conditions", []):
            self._concentration_check_dialog(target, dmg)

    def _con_save_mod(self, char: dict) -> int:
        """Return the CON saving throw modifier for a character."""
        saving_throws = char.get("Saving Throws") or {}
        for key in ("CONSTITUTION", "Con", "CON"):
            if key in saving_throws:
                return saving_throws[key]
        ability_scores = char.get("Ability Scores") or {}
        for key in ("Con", "CON", "CONSTITUTION"):
            if key in ability_scores:
                return (ability_scores[key] - 10) // 2
        return 0

    def _concentration_check_dialog(self, char: dict, dmg: int):
        """Show a modal concentration saving throw dialog."""
        dc = max(10, dmg // 2)
        con_mod = self._con_save_mod(char)
        name = char["name"]

        dialog = QDialog(self._window)
        dialog.setWindowTitle("Concentration Check")
        dialog.setModal(True)
        dialog.setStyleSheet(QSS)
        dialog.setFixedWidth(320)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # Gold header
        header_lbl = QLabel(f"{name} is concentrating!")
        header_lbl.setStyleSheet("color: #c9a84c; font-weight: bold; font-size: 13px;")
        header_lbl.setWordWrap(True)
        layout.addWidget(header_lbl)

        # DC info
        dc_lbl = QLabel(f"Damage taken: {dmg}  →  DC {dc}")
        dc_lbl.setObjectName("secondary")
        layout.addWidget(dc_lbl)

        mod_lbl = QLabel(f"CON save modifier: {con_mod:+d}")
        mod_lbl.setObjectName("secondary")
        layout.addWidget(mod_lbl)

        layout.addWidget(self._make_divider())

        # Roll input
        roll_input = QLineEdit()
        roll_input.setPlaceholderText("Enter roll total...")
        layout.addWidget(roll_input)

        # Result label (initially hidden)
        result_lbl = QLabel("")
        result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_lbl.setStyleSheet("font-weight: bold; font-size: 12px;")
        result_lbl.hide()
        layout.addWidget(result_lbl)

        def _update_result_label(text: str):
            if not text:
                result_lbl.hide()
                return
            try:
                roll = int(text)
            except ValueError:
                result_lbl.hide()
                return
            if roll >= dc:
                result_lbl.setStyleSheet(
                    "font-weight: bold; font-size: 12px; color: #2ecc71;"
                )
                result_lbl.setText("✓ CONCENTRATION MAINTAINED")
            else:
                result_lbl.setStyleSheet(
                    "font-weight: bold; font-size: 12px; color: #e74c3c;"
                )
                result_lbl.setText("✗ CONCENTRATION LOST")
            result_lbl.show()

        roll_input.textChanged.connect(_update_result_label)

        # Roll d20 button
        roll_btn = QPushButton("Roll d20")

        def _auto_roll():
            result = random.randint(1, 20) + con_mod
            roll_input.setText(str(result))
            if result >= dc:
                roll_input.setStyleSheet(
                    "background-color: #1a3a1a; border: 1px solid #2ecc71;"
                )
            else:
                roll_input.setStyleSheet(
                    "background-color: #3a1a1a; border: 1px solid #e74c3c;"
                )

        roll_btn.clicked.connect(_auto_roll)
        layout.addWidget(roll_btn)

        layout.addWidget(self._make_divider())

        # Confirm / Cancel row
        btn_row = QHBoxLayout()
        confirm_btn = QPushButton("Confirm")
        cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(confirm_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        def _confirm():
            text = roll_input.text().strip()
            if not text:
                return
            try:
                roll = int(text)
            except ValueError:
                return
            if roll < dc:
                if "Concentrating" in char.get("conditions", []):
                    char["conditions"].remove("Concentrating")
                self._log_event(f"{name} loses concentration (DC {dc}, rolled {roll})")
                self._refresh_selected_card()
            dialog.accept()

        def _cancel():
            dialog.reject()

        confirm_btn.clicked.connect(_confirm)
        cancel_btn.clicked.connect(_cancel)

        dialog.exec()

    def _apply_heal(self):
        if not self.target_character:
            return
        try:
            heal = int(self.heal_input.text())
        except ValueError:
            return

        char = self.target_character
        was_downed = self._char_death_state(char) != "alive"

        source = self.selected_character
        source_name = source["name"] if source is not None else None

        pre_hp = char["hp"]
        char["hp"] = min(char["hp"] + heal, char["max_hp"])
        actual_heal = char["hp"] - pre_hp

        char.setdefault("stats", _default_stats())
        char["stats"]["healing_received"] = char["stats"].get("healing_received", 0) + actual_heal
        if source is not None:
            source.setdefault("stats", _default_stats())
            source["stats"]["healing_done"] = source["stats"].get("healing_done", 0) + actual_heal

        self.history.append(
            (
                Action.HEAL,
                {
                    "heal": actual_heal,
                    "source_name": source_name,
                },
            )
        )

        if was_downed and char["hp"] > 0:
            char["death_saves_fail"] = 0
            char["death_saves_success"] = 0
            self._log_event(f"{char['name']} is resurrected with {char['hp']} HP")
        else:
            self._log_event(f"{char['name']} heals {heal} HP")

        # Auto-apply bloodied condition
        self._apply_bloodied_condition(char)

        self._rebuild_card(char)

    def _apply_failed_death_save(self, char: dict):
        if self._char_death_state(char) != "dying":
            return
        self._select_character(char)
        pre_fail = char.get("death_saves_fail", 0)
        char["death_saves_fail"] = min(pre_fail + 1, 3)
        newly_dead = pre_fail < 3 and char["death_saves_fail"] >= 3
        if newly_dead:
            char.setdefault("stats", _default_stats())
            char["stats"]["deaths"] = char["stats"].get("deaths", 0) + 1
        self.history.append((Action.DEATH_SAVE_FAIL, newly_dead))
        if char["death_saves_fail"] >= 3:
            self._log_event(f"{char['name']} has died (3 failed death saves)")
        else:
            self._log_event(
                f"{char['name']} fails a death save "
                f"({char['death_saves_fail']}/3 fails)"
            )
        self._refresh_selected_card()

    def _apply_success_death_save(self, char: dict):
        if self._char_death_state(char) != "dying":
            return
        self._select_character(char)
        char["death_saves_success"] = min(char.get("death_saves_success", 0) + 1, 3)
        self.history.append((Action.DEATH_SAVE_SUCCESS, None))
        if char["death_saves_success"] >= 3:
            self._log_event(f"{char['name']} stabilizes (3 successful death saves)")
        else:
            self._log_event(
                f"{char['name']} succeeds a death save "
                f"({char['death_saves_success']}/3 successes)"
            )
        self._refresh_selected_card()

    def _apply_temp_hp(self):
        if not self.selected_character:
            return
        try:
            amount = int(self.temp_hp_input.text())
        except ValueError:
            return

        old = self.selected_character.get("temp_hp", 0)
        self.selected_character["temp_hp"] = old + amount
        self._log_event(
            f"{self.selected_character['name']} gains {amount} temp HP "
            f"(total {self.selected_character['temp_hp']})"
        )
        self._refresh_selected_card()
