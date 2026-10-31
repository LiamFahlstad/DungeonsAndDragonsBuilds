"""Turns/initiative mixin for CombatAppQt."""

import random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
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

from Combat.PlayerLog import has_round_events

from .stats import _default_stats
from .styles import QSS
from Core.Rules import ability_modifier
from .state import CombatWindowState
from .undo import undoable


def initiative_units(chars: list[dict]) -> list[list[dict]]:
    """`chars` as the turns they take: each initiative group (the
    "initiative_group" its members share, at its first member's place) as
    one, and everyone else on their own."""
    units: list[list[dict]] = []
    groups: dict[str, list[dict]] = {}
    for char in chars:
        group = char.get("initiative_group")
        if group is None:
            units.append([char])
        elif group in groups:
            groups[group].append(char)
        else:
            groups[group] = [char]
            units.append(groups[group])
    return units


def unit_label(unit: list[dict]) -> str:
    """How the initiative screen names a turn: "Goblin Warriors (6)" for a
    group, the combatant's name otherwise."""
    group = unit[0].get("initiative_group")
    return f"{group} ({len(unit)})" if group else unit[0]["name"]


class TurnsMixin(CombatWindowState):
    """Mixin for turn and initiative management. An initiative group (see
    initiative_units) rolls once and stands together in initiative_order, so
    its members take one turn: current_turn_idx is its first member."""

    def _turn_span(self, idx: int) -> tuple[int, int]:
        """The slice [start, end) of initiative_order whose turn idx is in:
        its initiative group's run, or idx alone."""
        order = self.initiative_order
        group = order[idx].get("initiative_group")
        start, end = idx, idx + 1
        if group is None:
            return start, end
        while start > 0 and order[start - 1].get("initiative_group") == group:
            start -= 1
        while end < len(order) and order[end].get("initiative_group") == group:
            end += 1
        return start, end

    def _current_turn_group(self) -> list[dict]:
        """Everyone whose turn it is (the active combatant's initiative group,
        or just them); [] outside combat."""
        if self.phase != "COMBAT" or not self.initiative_order:
            return []
        start, end = self._turn_span(self.current_turn_idx)
        return self.initiative_order[start:end]

    def _is_last_turn(self) -> bool:
        if not self.initiative_order:
            return True
        return self._turn_span(self.current_turn_idx)[1] >= len(self.initiative_order)

    @undoable
    def _advance_turn(self):
        """Combined Next Combatant / Next Round button handler. With the "skip
        dead" setting on, it passes over turns where everyone is dead (at most
        once round the order, in case the whole fight is)."""
        for _ in initiative_units(self.initiative_order):
            self._pass_turn()
            if not (self.settings.skip_dead_turns and self._turn_is_dead()):
                break
        self._refresh_turn()
        self._on_turn_changed()
        # Save whose turn it is, so continuing the fight starts there. A log
        # without events is still as prepared, and stays that way.
        data = self._read_log()
        if has_round_events(data):
            self._write_log(data)

    def _turn_is_dead(self) -> bool:
        """Whether everyone whose turn it is is dead. Someone dying still has
        a turn: it's when they make their death save."""
        return all(
            self._char_death_state(c) == "dead" for c in self._current_turn_group()
        )

    def _upcoming_turns(self) -> list[list[dict]]:
        """The turns after this one, soonest first, once round the order,
        leaving out the ones Next would pass over."""
        order = self.initiative_order
        turns = []
        start = 0
        while start < len(order):
            span_end = self._turn_span(start)[1]
            turns.append(order[start:span_end])
            start = span_end
        now = next(
            i
            for i, turn in enumerate(turns)
            if any(c is order[self.current_turn_idx] for c in turn)
        )
        upcoming = turns[now + 1 :] + turns[:now]
        if not self.settings.skip_dead_turns:
            return upcoming
        return [
            turn
            for turn in upcoming
            if any(self._char_death_state(c) != "dead" for c in turn)
        ]

    def _pass_turn(self):
        """Move on one turn: its round, and what the turn passing ticks. A
        skipped turn passes like any other, so durations stay right."""
        ended = self._current_turn_group()
        new_round = self._is_last_turn()
        if not new_round:
            self.current_turn_idx = self._turn_span(self.current_turn_idx)[1]
        else:
            self.round_number += 1
            self.current_turn_idx = 0
            self._log_event(f"--- Round {self.round_number} ---", note_turn=False)
            self.round_label.setText(f"Round {self.round_number}")
            self._tick_active_spells()
            self._tick_active_features()
        # The action economy (Action/Bonus Action/Reaction) resets for whoever's
        # turn is now starting — other combatants keep their tallies until theirs does.
        self._turn_start_notes = []
        for new_active in self._current_turn_group():
            new_active["action_uses"] = {}
            if self._char_death_state(new_active) != "dead":
                self._start_monster_turn(new_active)
            self._rebuild_card(new_active)
        self._tick_timed_conditions(ended, self._current_turn_group(), new_round)

    def _is_first_turn(self) -> bool:
        """Whether it's round 1's first turn, so there is no turn before it."""
        return self.round_number <= 1 and (
            not self.initiative_order or self._turn_span(self.current_turn_idx)[0] == 0
        )

    def _previous_turn(self):
        """Previous button handler: take back a Next press made by mistake.
        Straight after Next, that press is undone (its round, timer ticks and
        reset action tallies included); after anything else, only whose turn
        it is steps back."""
        if self.phase != "COMBAT" or self._is_first_turn():
            return
        if self.history and self.history[-1].operation == "_advance_turn":
            self._undo_last()
        else:
            self._step_turn_back()

    @undoable
    def _step_turn_back(self):
        """Make it the previous turn's (the last one of the round before, from
        a round's first turn), changing nothing else. With the "skip dead"
        setting on, that's the last turn Next wouldn't have passed over."""
        for _ in initiative_units(self.initiative_order):
            start = self._turn_span(self.current_turn_idx)[0]
            if start > 0:
                self.current_turn_idx = self._turn_span(start - 1)[0]
            else:
                self.round_number -= 1
                self.current_turn_idx = self._turn_span(len(self.initiative_order) - 1)[
                    0
                ]
                self.round_label.setText(f"Round {self.round_number}")
            skip = self.settings.skip_dead_turns and self._turn_is_dead()
            if not skip or self._is_first_turn():
                break
        self._refresh_turn()
        self._on_turn_changed()
        data = self._read_log()
        if has_round_events(data):
            self._write_log(data)

    def _shortcut_next_turn(self):
        """Keyboard shortcut 'Enter': Next Combatant / Next Round, only once combat has
        started and no text field is focused (Enter in an input field should only submit
        that field, not also advance the turn)."""
        if self.phase != "COMBAT":
            return
        if isinstance(QApplication.focusWidget(), QLineEdit):
            return
        self._advance_turn()

    def _shortcut_previous_turn(self):
        """Keyboard shortcut 'Shift+Enter': the Previous button, under the
        same conditions as Enter."""
        if isinstance(QApplication.focusWidget(), QLineEdit):
            return
        self._previous_turn()

    def _on_turn_changed(self):
        """Apply the turn settings (settings.py) when whose turn it is changes:
        Next, Previous, combat starting or continuing, an undo across a turn."""
        # A roll and a save were for the turn that's over.
        if self._rolled_damage_text == self.damage_input.text():
            self.damage_input.clear()
        self._rolled_damage_text = ""
        if self._saved_targets:
            self._saved_targets = []
            self._set_targets(list(self.target_characters))
        self._follow_turn_with_source()
        active = self._current_turn_character()
        if self.settings.clear_targets_on_turn and self.target_characters:
            self._set_targets([])
        if self.settings.restart_player_timer_on_turn:
            self._reset_player_timer()
            if active is not None and active.get("_is_player"):
                self._start_player_timer()
        self._action_result_label.setText("")
        self._take_turn_reminders()
        self._refresh_views()

    def _follow_turn_with_source(self):
        """With the "source follows the turn" setting on, make whoever's turn
        it is the source (an initiative group's first member). Picking another
        source by hand lasts until the turn changes."""
        active = self._current_turn_character()
        if self.settings.source_follows_turn and active is not None:
            self._select_character(active)

    @staticmethod
    def _dex_mod(char: dict) -> int:
        ability_scores = char.get("Ability Scores") or {}
        for key in ("DEXTERITY", "Dexterity", "Dex", "DEX"):
            if key in ability_scores:
                return ability_modifier(ability_scores[key])
        return 0

    def _add_initiative_row(self, unit: list[dict]):
        """Build and append one initiative-entry row for unit (one combatant,
        or an initiative group, which rolls once with its first member's
        modifier). Used both while building the initiative screen from scratch
        and to append a row for a combatant added mid-setup via Add Combatant."""
        char = unit[0]
        mod = self._dex_mod(char)

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        name_lbl = QLabel(unit_label(unit))
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
        init_input.returnPressed.connect(self._initiative_enter_pressed)
        row_layout.addWidget(init_input)

        roll_btn = QPushButton("Roll")
        roll_btn.setFixedWidth(50)

        def _roll(checked=False, inp=init_input, m=mod):
            result = random.randint(1, 20) + m
            inp.setText(str(result))
            inp.setStyleSheet("background-color: #1a3a1a; border: 1px solid #2ecc71;")

        roll_btn.clicked.connect(_roll)
        row_layout.addWidget(roll_btn)

        if self._hp_not_set(char):
            # Summons (Draconic Spirit, Beast of the Land, ...) have no HP in
            # their stat block because the spell or feature sets it, so the GM
            # enters it here before combat starts.
            row_layout.addWidget(QLabel("HP:"))
            hp_input = QLineEdit()
            hp_input.setPlaceholderText(char.get("hp_formula") or "Max HP...")
            hp_input.setFixedWidth(80)
            hp_input.textChanged.connect(self._check_start_button)
            hp_input.returnPressed.connect(self._initiative_enter_pressed)
            row_layout.addWidget(hp_input)
            for member in unit:
                self._initiative_hp_inputs[id(member)] = hp_input

        row_layout.addStretch()
        self._initiative_rows_layout.addWidget(row_widget)

        for member in unit:
            self._initiative_inputs[id(member)] = init_input

    @undoable
    def _add_ad_hoc_combatant(self, name: str, hp: int = 10, ac: int = 10):
        """Quickly add a free-text combatant mid-session (e.g. a door, an
        improvised target) without needing a full character sheet or a
        predefined monster. Slots into whichever phase is currently active:
        appended to the initiative-entry screen before combat starts, or
        appended to the end of the turn order (it'll get a turn once the
        order cycles round to it) once combat is underway."""
        char = {
            "name": name,
            "create_name": name,
            "hp": hp,
            "max_hp": hp,
            "ac": ac,
            "temp_hp": 0,
            "conditions": [],
            "visibility_states": [],
            "death_saves_fail": 0,
            "death_saves_success": 0,
            "stats": _default_stats(),
            "spell_slots": {},
            "Ability Scores": {},
            "Saving Throws": {},
        }
        self.characters.append(char)
        self._log_event(f"{name} added to the encounter", note_turn=False)
        if self.phase == "COMBAT":
            self.initiative_order.append(char)
            self._rebuild_cards()
        else:
            self._add_initiative_row([char])
            self._check_start_button()

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
        self._initiative_hp_inputs.clear()

        self._initiative_rows_layout = QVBoxLayout()
        self._initiative_rows_layout.setSpacing(8)
        outer.addLayout(self._initiative_rows_layout)

        for unit in initiative_units(self.characters):
            self._add_initiative_row(unit)

        outer.addWidget(self._make_divider())

        roll_all_btn = QPushButton("Roll for All")
        roll_all_btn.setStyleSheet(
            "background-color: #1a2a3a; border: 1px solid #5bc8f5;"
            " color: #5bc8f5; font-weight: bold; min-height: 26px;"
        )

        def _roll_all():
            for unit in initiative_units(self.characters):
                self._roll_initiative(unit)
            self._check_start_button()

        roll_all_btn.clicked.connect(_roll_all)

        roll_monsters_btn = QPushButton("Roll for Monsters")
        roll_monsters_btn.setStyleSheet(roll_all_btn.styleSheet())
        roll_monsters_btn.setToolTip(
            "Roll every monster's initiative that isn't filled in, then jump to"
            " the first player's field"
        )
        roll_monsters_btn.clicked.connect(self._roll_monster_initiative)

        roll_row = QHBoxLayout()
        roll_row.addWidget(roll_monsters_btn)
        roll_row.addWidget(roll_all_btn)
        outer.addLayout(roll_row)

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

    def _roll_initiative(self, unit: list[dict]):
        result = random.randint(1, 20) + self._dex_mod(unit[0])
        inp = self._initiative_inputs[id(unit[0])]
        inp.setText(str(result))
        inp.setStyleSheet("background-color: #1a3a1a; border: 1px solid #2ecc71;")

    def _roll_monster_initiative(self):
        """Roll for everyone but the players, who roll their own dice."""
        for unit in initiative_units(self.characters):
            if not (
                unit[0].get("_is_player")
                or self._initiative_inputs[id(unit[0])].text().strip()
            ):
                self._roll_initiative(unit)
        self._check_start_button()
        self._focus_next_initiative_field()

    def _focus_next_initiative_field(self) -> bool:
        """Put the cursor in the first field still needing a number, if any."""
        for inp in self._initiative_inputs.values():
            if not self._is_int(inp.text()):
                inp.setFocus()
                return True
        for inp in self._initiative_hp_inputs.values():
            if self._positive_int(inp.text()) is None:
                inp.setFocus()
                return True
        return False

    def _initiative_enter_pressed(self):
        """Enter in a field: on to the next one, or into the fight once
        they're all filled in."""
        if not self._focus_next_initiative_field():
            self._start_combat()

    @staticmethod
    def _is_int(text: str) -> bool:
        try:
            int(text)
        except ValueError:
            return False
        return True

    @staticmethod
    def _hp_not_set(char: dict) -> bool:
        """True for a combatant whose stat block leaves HP to the spell or
        feature that summons it (max HP 0), until the GM enters it."""
        return char.get("max_hp", 1) <= 0

    @staticmethod
    def _positive_int(text: str) -> int | None:
        try:
            value = int(text)
        except ValueError:
            return None
        return value if value > 0 else None

    def _check_start_button(self):
        """Enable Start Combat only when all fields have a numeric value and
        every HP field a positive one."""
        all_filled = True
        for inp in self._initiative_inputs.values():
            if not self._is_int(inp.text()):
                all_filled = False
                break
        for inp in self._initiative_hp_inputs.values():
            if self._positive_int(inp.text()) is None:
                all_filled = False
                break
        self._start_combat_btn.setEnabled(all_filled)

    def _start_combat(self):
        """Parse initiatives, sort characters, and switch to combat phase."""
        for char in self.characters:
            hp_input = self._initiative_hp_inputs.get(id(char))
            if hp_input is None:
                continue
            hp = self._positive_int(hp_input.text())
            if hp is not None:
                char["hp"] = char["max_hp"] = hp

        # An initiative group is sorted (and tie-broken) as one, so its
        # members stay together and take one turn.
        order_with_initiative: list[tuple[int, list[dict]]] = []
        for unit in initiative_units(self.characters):
            inp = self._initiative_inputs[id(unit[0])]
            try:
                value = int(inp.text())
            except ValueError:
                value = 0
            order_with_initiative.append((value, unit))

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

        if tied_groups and self.settings.ask_initiative_ties:
            resolved = self._show_tie_break_dialog(order_with_initiative, tied_groups)
            if resolved is None:
                return  # user cancelled — stay on initiative screen
            order_with_initiative = resolved
        elif tied_groups:
            order_with_initiative.sort(
                key=lambda x: (x[0], self._dex_mod(x[1][0])), reverse=True
            )

        sorted_chars = [c for _, unit in order_with_initiative for c in unit]

        # Re-order self.characters in-place to match initiative order
        self.characters[:] = sorted_chars
        self.initiative_order = list(sorted_chars)
        self.current_turn_idx = 0
        self.phase = "COMBAT"

        self._switch_to_combat()

    def _show_tie_break_dialog(
        self,
        order_with_initiative: list[tuple[int, list[dict]]],
        tied_groups: list[tuple[int, int, int]],
    ) -> list[tuple[int, list[dict]]] | None:
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
            for _, unit in order_with_initiative[start:end]:
                item = QListWidgetItem(unit_label(unit))
                item.setData(Qt.ItemDataRole.UserRole, unit)
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
        for start, _end, lw in list_widgets:
            init_val = result[start][0]
            for i in range(lw.count()):
                item = lw.item(i)
                assert item is not None, i
                unit = item.data(Qt.ItemDataRole.UserRole)
                result[start + i] = (init_val, unit)

        return result

    def _switch_to_combat(self):
        """Replace the initiative widget with the card grid and update the panel."""
        # Swap scroll area content (the initiative screen or the party view)
        old = self._scroll_area.takeWidget()
        if old is not None and old is not self._cards_container:
            old.deleteLater()
        self._initiative_widget = None

        self._scroll_area.setWidget(self._cards_container)
        self._cards_container.show()

        # Show the combat-only panel widgets
        self._init_tracker_container.show()
        self._turn_divider.show()
        self._prev_turn_btn.show()
        self._next_turn_btn.show()
        self._turn_panel.show()

        self._rebuild_cards()
        self._refresh_turn()
        self._refresh_rest_buttons()
        self._on_turn_changed()

    def _switch_to_initiative(self):
        """Show a fresh initiative-entry screen for self.characters, in place
        of the card grid (or of the previous initiative screen)."""
        old = self._scroll_area.takeWidget()
        if old is not None and old is not self._cards_container:
            old.deleteLater()
        self._cards_container.hide()

        # Hide the combat-only panel widgets
        self._init_tracker_container.hide()
        self._turn_divider.hide()
        self._prev_turn_btn.hide()
        self._next_turn_btn.hide()
        self._turn_panel.hide()

        self._initiative_widget = self._build_initiative_widget()
        self._scroll_area.setWidget(self._initiative_widget)
        self._refresh_rest_buttons()
        self._focus_next_initiative_field()

    def _refresh_initiative_tracker(self):
        """Update the turn counter label, counting an initiative group as one
        turn."""
        if not self.initiative_order:
            return

        turn_starts = []
        idx = 0
        while idx < len(self.initiative_order):
            turn_starts.append(idx)
            idx = self._turn_span(idx)[1]
        turn = sum(1 for start in turn_starts if start <= self.current_turn_idx)
        self._turn_counter_label.setText(f"Turn {turn} / {len(turn_starts)}")

    def _refresh_next_button(self):
        """Say what pressing Next will do, turns it would pass over included:
        the last living combatant's Next starts the round."""
        later = self.initiative_order[self._turn_span(self.current_turn_idx)[1] :]
        if self.settings.skip_dead_turns:
            ends_round = all(self._char_death_state(c) == "dead" for c in later)
        else:
            ends_round = not later
        self._next_turn_btn.setText("Next Round" if ends_round else "Next Combatant")

    def _refresh_turn(self):
        """Update the active-turn highlight, tracker, and Next/Previous buttons."""
        self._refresh_cards()
        self._refresh_initiative_tracker()
        self._prev_turn_btn.setEnabled(not self._is_first_turn())
        if self.initiative_order:
            self._refresh_next_button()
            # Auto-scroll to active card
            active_char = self.initiative_order[self.current_turn_idx]
            card = self._card_widgets.get(id(active_char))
            if card and self.settings.scroll_to_active_card:
                self._scroll_area.ensureWidgetVisible(card)
