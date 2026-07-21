"""Turns/initiative mixin for CombatAppQt."""

import random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .styles import QSS


class TurnsMixin:
    """Mixin for turn and initiative management."""

    def _advance_turn(self):
        """Combined Next Combatant / Next Round button handler."""
        last_idx = len(self.initiative_order) - 1
        if self.current_turn_idx < last_idx:
            self.current_turn_idx += 1
        else:
            self.round_number += 1
            self.current_turn_idx = 0
            self._log_event(f"--- Round {self.round_number} ---", note_turn=False)
            self.round_label.setText(f"Round {self.round_number}")
            self._tick_active_spells()
        if self.initiative_order:
            # The action economy (Action/Bonus Action/Reaction) resets for whoever's
            # turn is now starting — other combatants keep their tallies until theirs does.
            new_active = self.initiative_order[self.current_turn_idx]
            new_active["action_uses"] = {}
            self._rebuild_card(new_active)
        self._refresh_turn()

    def _shortcut_next_turn(self):
        """Keyboard shortcut 'Enter': Next Combatant / Next Round, only once combat has started."""
        if self.phase == "COMBAT":
            self._advance_turn()

    @staticmethod
    def _dex_mod(char: dict) -> int:
        ability_scores = char.get("Ability Scores") or {}
        for key in ("DEXTERITY", "Dexterity", "Dex", "DEX"):
            if key in ability_scores:
                return (ability_scores[key] - 10) // 2
        return 0

    def _build_initiative_widget(self) -> QWidget:
        """Build the initiative-entry screen."""
        container = QWidget()
        container.setObjectName("initiativeContainer")
        outer = QVBoxLayout(container)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        header = QLabel("Roll Initiative")
        header.setStyleSheet("color: #c9a84c; font-size: 16px; font-weight: bold;")
        outer.addWidget(header)

        outer.addWidget(self._make_divider())

        self._initiative_inputs.clear()

        for char in self.characters:
            mod = self._dex_mod(char)

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            name_lbl = QLabel(char["name"])
            name_lbl.setStyleSheet("color: #c9a84c; font-weight: bold;")
            name_lbl.setFixedWidth(160)
            row_layout.addWidget(name_lbl)

            mod_lbl = QLabel(f"(mod {mod:+d})")
            mod_lbl.setObjectName("secondary")
            mod_lbl.setFixedWidth(60)
            row_layout.addWidget(mod_lbl)

            init_input = QLineEdit()
            init_input.setPlaceholderText("Total...")
            init_input.setFixedWidth(60)
            init_input.textChanged.connect(self._check_start_button)
            row_layout.addWidget(init_input)

            roll_btn = QPushButton("Roll")
            roll_btn.setFixedWidth(50)

            def _roll(checked=False, inp=init_input, m=mod):
                result = random.randint(1, 20) + m
                inp.setText(str(result))
                inp.setStyleSheet(
                    "background-color: #1a3a1a; border: 1px solid #2ecc71;"
                )

            roll_btn.clicked.connect(_roll)
            row_layout.addWidget(roll_btn)

            row_layout.addStretch()
            outer.addWidget(row_widget)

            self._initiative_inputs[id(char)] = init_input

        outer.addWidget(self._make_divider())

        roll_all_btn = QPushButton("Roll for All")
        roll_all_btn.setStyleSheet(
            "background-color: #1a2a3a; border: 1px solid #5bc8f5;"
            " color: #5bc8f5; font-weight: bold; min-height: 26px;"
        )

        def _roll_all():
            for char, inp in (
                (c, self._initiative_inputs[id(c)]) for c in self.characters
            ):
                result = random.randint(1, 20) + self._dex_mod(char)
                inp.setText(str(result))
                inp.setStyleSheet(
                    "background-color: #1a3a1a; border: 1px solid #2ecc71;"
                )
            self._check_start_button()

        roll_all_btn.clicked.connect(_roll_all)
        outer.addWidget(roll_all_btn)

        self._start_combat_btn = QPushButton("Start Combat")
        self._start_combat_btn.setEnabled(False)
        self._start_combat_btn.setStyleSheet(
            "background-color: #1a3a1a; border: 1px solid #2ecc71;"
            " color: #2ecc71; font-weight: bold; min-height: 30px;"
        )
        self._start_combat_btn.clicked.connect(self._start_combat)
        outer.addWidget(self._start_combat_btn)

        outer.addStretch()
        return container

    def _check_start_button(self):
        """Enable Start Combat only when all fields have a numeric value."""
        all_filled = True
        for inp in self._initiative_inputs.values():
            try:
                int(inp.text())
            except ValueError:
                all_filled = False
                break
        self._start_combat_btn.setEnabled(all_filled)

    def _start_combat(self):
        """Parse initiatives, sort characters, and switch to combat phase."""
        order_with_initiative = []
        for char in self.characters:
            inp = self._initiative_inputs[id(char)]
            try:
                value = int(inp.text())
            except ValueError:
                value = 0
            order_with_initiative.append((value, char))

        # Stable sort descending — ties preserve original order
        order_with_initiative.sort(key=lambda x: x[0], reverse=True)

        # Detect tie groups (contiguous runs with same initiative value)
        tied_groups: list[tuple[int, int, int]] = []  # (init_val, start_idx, end_idx)
        i = 0
        while i < len(order_with_initiative):
            j = i + 1
            while (
                j < len(order_with_initiative)
                and order_with_initiative[j][0] == order_with_initiative[i][0]
            ):
                j += 1
            if j - i > 1:
                tied_groups.append((order_with_initiative[i][0], i, j))
            i = j

        if tied_groups:
            resolved = self._show_tie_break_dialog(order_with_initiative, tied_groups)
            if resolved is None:
                return  # user cancelled — stay on initiative screen
            order_with_initiative = resolved

        sorted_chars = [c for _, c in order_with_initiative]

        # Re-order self.characters in-place to match initiative order
        self.characters[:] = sorted_chars
        self.initiative_order = list(sorted_chars)
        self.current_turn_idx = 0
        self.phase = "COMBAT"

        self._switch_to_combat()

    def _show_tie_break_dialog(
        self,
        order_with_initiative: list[tuple[int, dict]],
        tied_groups: list[tuple[int, int, int]],
    ) -> list[tuple[int, dict]] | None:
        """Show a dialog to resolve initiative ties via drag-and-drop.
        Returns the updated order list, or None if the user went back."""
        dlg = QDialog(self._window)
        dlg.setWindowTitle("Resolve Initiative Ties")
        dlg.setMinimumWidth(360)
        dlg.setStyleSheet(QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        info = QLabel(
            "Some combatants tied on initiative.\nDrag rows to set the turn order within each tied group."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #a0a0b0;")
        layout.addWidget(info)

        list_widgets: list[tuple[int, int, QListWidget]] = []

        for init_val, start, end in tied_groups:
            grp_label = QLabel(f"Initiative {init_val}")
            grp_label.setStyleSheet("font-weight: bold; color: #c9a84c;")
            layout.addWidget(grp_label)

            lw = QListWidget()
            lw.setDragDropMode(QListWidget.DragDropMode.InternalMove)
            lw.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
            lw.setFixedHeight((end - start) * 32 + 4)
            lw.setStyleSheet(
                "QListWidget { background: #16213e; border: 1px solid #0f3460; }"
                "QListWidget::item { padding: 5px 10px; }"
                "QListWidget::item:selected { background: #1e2d5a; color: #eaeaea; }"
            )
            for _, char in order_with_initiative[start:end]:
                item = QListWidgetItem(char["name"])
                item.setData(Qt.ItemDataRole.UserRole, char)
                lw.addItem(item)

            layout.addWidget(lw)
            list_widgets.append((start, end, lw))

        btn_row = QHBoxLayout()
        back_btn = QPushButton("Go Back")
        ok_btn = QPushButton("Start Combat")
        back_btn.clicked.connect(dlg.reject)
        ok_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(back_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return None

        result = list(order_with_initiative)
        for start, end, lw in list_widgets:
            init_val = result[start][0]
            for i in range(lw.count()):
                char = lw.item(i).data(Qt.ItemDataRole.UserRole)
                result[start + i] = (init_val, char)

        return result

    def _switch_to_combat(self):
        """Replace the initiative widget with the card grid and update the panel."""
        # Swap scroll area content
        self._scroll_area.takeWidget()
        if self._initiative_widget is not None:
            self._initiative_widget.deleteLater()
            self._initiative_widget = None

        self._scroll_area.setWidget(self._cards_container)
        self._cards_container.show()

        # Show the combat-only panel widgets
        self._init_tracker_container.show()
        self._turn_divider.show()
        self._next_turn_btn.show()

        self._rebuild_cards()
        self._refresh_turn()

    def _refresh_initiative_tracker(self):
        """Update the turn counter label."""
        if not self.initiative_order:
            return

        total = len(self.initiative_order)
        self._turn_counter_label.setText(f"Turn {self.current_turn_idx + 1} / {total}")

    def _refresh_turn(self):
        """Update the active-turn highlight, tracker, and Next button label."""
        self._refresh_cards()
        self._refresh_initiative_tracker()
        if self.initiative_order:
            last_idx = len(self.initiative_order) - 1
            if self.current_turn_idx < last_idx:
                self._next_turn_btn.setText("Next Combatant")
            else:
                self._next_turn_btn.setText("Next Round")
            # Auto-scroll to active card
            active_char = self.initiative_order[self.current_turn_idx]
            card = self._card_widgets.get(id(active_char))
            if card:
                self._scroll_area.ensureWidgetVisible(card)
