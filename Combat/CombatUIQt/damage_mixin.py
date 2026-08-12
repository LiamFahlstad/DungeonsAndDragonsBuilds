"""Damage/healing mixin for CombatAppQt."""

import random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from Combat.Definitions import Action
from .stats import _default_stats
from .styles import QSS


def _damage_type_value(t) -> str:
    return t.value if hasattr(t, "value") else str(t)


def _entry_damage_types(entry) -> list:
    if isinstance(entry, dict):
        return entry.get("damage_types", [])
    return getattr(entry, "damage_types", [])


class DamageMixin:
    """Mixin for damage and healing related methods."""

    def _damage_type_modifier(self, target: dict, dmg: int, damage_type: str):
        """Check target's damage immunities/resistances/vulnerabilities against
        damage_type and return (applied_dmg, outcome), outcome being one of
        'immune', 'resisted', 'vulnerable', or None."""

        def has_type(entries) -> bool:
            for entry in entries or []:
                if any(_damage_type_value(t) == damage_type for t in _entry_damage_types(entry)):
                    return True
            return False

        if has_type(target.get("damage_immunities")):
            return 0, "immune"
        if has_type(target.get("damage_resistances")):
            return dmg // 2, "resisted"
        if has_type(target.get("damage_vulnerabilities")):
            return dmg * 2, "vulnerable"
        return dmg, None

    def _apply_bloodied_condition(self, char: dict, source: dict | None = None):
        """Auto-apply/remove Bloodied condition based on HP threshold. Pass
        `source` (the damage dealer/healer) to log the change with a source,
        same as any other condition; omit it for silent resyncs (undo, replay)."""
        max_hp = char.get("max_hp", 1)
        hp = char.get("hp", 0)
        is_bloodied = "Bloodied" in char.get("conditions", [])
        should_be_bloodied = hp > 0 and hp <= max_hp / 2

        if should_be_bloodied and not is_bloodied:
            if source is not None:
                self._add_condition_to(char, "Bloodied", source=source)
            else:
                char["conditions"].append("Bloodied")
        elif not should_be_bloodied and is_bloodied:
            if source is not None:
                self._remove_condition_from(char, "Bloodied", source=source)
            else:
                char["conditions"].remove("Bloodied")

    def _apply_damage(self):
        """Apply damage as-is, with no resistance/vulnerability/immunity checks."""
        self._do_apply_damage(check_resistance=False)

    def _apply_damage_checked(self):
        """Apply damage after checking the target's resistances/vulnerabilities/immunities
        against the selected damage type."""
        self._do_apply_damage(check_resistance=True)

    def _do_apply_damage(self, check_resistance: bool):
        if not self.target_characters:
            return
        try:
            dmg_input = int(self.damage_input.text())
        except ValueError:
            return

        source = self.selected_character or self._current_turn_character()
        source_name = source["name"] if source is not None else None

        damage_type = self.damage_type_combo.currentData()

        if damage_type is None:
            QMessageBox.warning(self._window, "Error", "Select a damage type before applying damage.")
            return

        for target in list(self.target_characters):
            dmg = dmg_input
            outcome = None
            if check_resistance and damage_type is not None:
                dmg, outcome = self._damage_type_modifier(target, dmg, damage_type)

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

            damage_value = {
                "hp_delta": hp_delta,
                "temp_delta": temp_delta,
                "dmg": dmg,
                "damage_type": damage_type,
                "source_name": source_name,
                "target_name": target["name"],
                "knockout": knockout,
                "outcome": outcome,
            }
            self.history.append((Action.DAMAGE, damage_value))
            type_prefix = f" {damage_type}" if damage_type else ""
            source_suffix = f" from {source_name}" if source_name else ""
            outcome_suffix = f" ({outcome})" if outcome else ""
            self._log_event(
                f"{target['name']} takes {dmg}{type_prefix} damage{source_suffix}{outcome_suffix}",
                character=target["name"],
                action=Action.DAMAGE,
                value=damage_value,
            )

            # Auto-apply bloodied condition, attributed to whoever dealt the damage
            self._apply_bloodied_condition(target, source=source)

            self._rebuild_card(target)

            if "Concentrating" in target.get("conditions", []):
                self._concentration_check_dialog(target, dmg)

        self.damage_type_combo.setCurrentIndex(0)

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
                # Concentration is always lost by the caster's own failed save,
                # so the caster is both source and target here.
                cond_value = {
                    "condition": "Concentrating",
                    "source_name": name,
                    "target_name": name,
                }
                self.history.append((Action.REMOVE_CONDITION, cond_value))
                self._log_event(
                    f"{name} loses concentration (DC {dc}, rolled {roll})",
                    character=name,
                    action=Action.REMOVE_CONDITION,
                    value=cond_value,
                )
                self._refresh_selected_card()
            dialog.accept()

        def _cancel():
            dialog.reject()

        confirm_btn.clicked.connect(_confirm)
        cancel_btn.clicked.connect(_cancel)

        dialog.exec()

    def _apply_heal(self):
        if not self.target_characters:
            return
        try:
            heal = int(self.heal_input.text())
        except ValueError:
            return

        source = self.selected_character or self._current_turn_character()
        source_name = source["name"] if source is not None else None

        for char in list(self.target_characters):
            was_downed = self._char_death_state(char) != "alive"

            pre_hp = char["hp"]
            char["hp"] = min(char["hp"] + heal, char["max_hp"])
            actual_heal = char["hp"] - pre_hp

            char.setdefault("stats", _default_stats())
            char["stats"]["healing_received"] = char["stats"].get("healing_received", 0) + actual_heal
            if source is not None:
                source.setdefault("stats", _default_stats())
                source["stats"]["healing_done"] = source["stats"].get("healing_done", 0) + actual_heal

            heal_value = {"heal": actual_heal, "source_name": source_name, "target_name": char["name"]}
            self.history.append((Action.HEAL, heal_value))

            source_suffix = f" from {source_name}" if source_name else ""

            if was_downed and char["hp"] > 0:
                char["death_saves_fail"] = 0
                char["death_saves_success"] = 0
                self._log_event(
                    f"{char['name']} is resurrected with {char['hp']} HP{source_suffix}",
                    character=char["name"],
                    action=Action.HEAL,
                    value=heal_value,
                )
            else:
                self._log_event(
                    f"{char['name']} heals {actual_heal} HP{source_suffix}",
                    character=char["name"],
                    action=Action.HEAL,
                    value=heal_value,
                )

            # Auto-apply bloodied condition, attributed to whoever healed
            self._apply_bloodied_condition(char, source=source)

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
            self._log_event(
                f"{char['name']} has died (3 failed death saves)",
                character=char["name"],
                action=Action.DEATH_SAVE_FAIL,
                value=newly_dead,
            )
        else:
            self._log_event(
                f"{char['name']} fails a death save "
                f"({char['death_saves_fail']}/3 fails)",
                character=char["name"],
                action=Action.DEATH_SAVE_FAIL,
                value=newly_dead,
            )
        self._refresh_selected_card()

    def _apply_success_death_save(self, char: dict):
        if self._char_death_state(char) != "dying":
            return
        self._select_character(char)
        char["death_saves_success"] = min(char.get("death_saves_success", 0) + 1, 3)
        self.history.append((Action.DEATH_SAVE_SUCCESS, None))
        if char["death_saves_success"] >= 3:
            self._log_event(
                f"{char['name']} stabilizes (3 successful death saves)",
                character=char["name"],
                action=Action.DEATH_SAVE_SUCCESS,
                value=None,
            )
        else:
            self._log_event(
                f"{char['name']} succeeds a death save "
                f"({char['death_saves_success']}/3 successes)",
                character=char["name"],
                action=Action.DEATH_SAVE_SUCCESS,
                value=None,
            )
        self._refresh_selected_card()

    def _apply_temp_hp(self):
        if not self.target_characters:
            return
        try:
            amount = int(self.temp_hp_input.text())
        except ValueError:
            return

        source = self.selected_character or self._current_turn_character()
        source_name = source["name"] if source is not None else None

        for target in list(self.target_characters):
            old = target.get("temp_hp", 0)
            target["temp_hp"] = old + amount

            target.setdefault("stats", _default_stats())
            target["stats"]["temp_hp_received"] = target["stats"].get("temp_hp_received", 0) + amount
            if source is not None:
                source.setdefault("stats", _default_stats())
                source["stats"]["temp_hp_granted"] = source["stats"].get("temp_hp_granted", 0) + amount

            temp_hp_value = {"amount": amount, "source_name": source_name, "target_name": target["name"]}
            self.history.append((Action.ADD_TEMP_HP, temp_hp_value))

            source_suffix = f" from {source_name}" if source_name else ""
            self._log_event(
                f"{target['name']} gains {amount} temp HP{source_suffix} "
                f"(total {target['temp_hp']})",
                character=target["name"],
                action=Action.ADD_TEMP_HP,
                value=temp_hp_value,
            )
            self._rebuild_card(target)
