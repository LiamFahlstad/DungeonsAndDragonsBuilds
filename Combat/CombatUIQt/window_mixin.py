"""Window/UI construction mixin for CombatAppQt."""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import DamageType
from Core.Definitions import get_damage_type_color
from .styles import QSS


class WindowMixin:
    """Mixin for window building and selection logic."""

    def _select_character(self, char: dict):
        self.selected_character = char
        self.selected_label.setText(f"Source: {char['name']}")
        self._more_info_btn.setEnabled(True)
        self._cast_spell_btn.setEnabled(True)
        self._refresh_cards()

    def _select_target_character(self, char: dict, additive: bool = False):
        if additive:
            if any(char is t for t in self.target_characters):
                self.target_characters = [t for t in self.target_characters if t is not char]
            else:
                self.target_characters.append(char)
        else:
            self.target_characters = [char]
        self._update_target_label()
        self._refresh_cards()

    def _update_target_label(self):
        if not self.target_characters:
            self.target_label.setText("Target: None")
        elif len(self.target_characters) == 1:
            self.target_label.setText(f"Target: {self.target_characters[0]['name']}")
        else:
            names = ", ".join(t["name"] for t in self.target_characters)
            self.target_label.setText(f"Targets: {names}")

    def _clear_selection(self):
        self.selected_character = None
        self.selected_label.setText("Source: None")
        self._more_info_btn.setEnabled(False)
        self._cast_spell_btn.setEnabled(False)
        self.target_characters = []
        self.target_label.setText("Target: None")
        self._refresh_cards()

    def _update_combo_sensitive_shortcuts(self, _old, new):
        """Disable every combo-sensitive shortcut while a combo box has focus,
        re-enable otherwise. A registered QShortcut consumes a matching key
        event before it ever reaches the focused widget, no matter what its
        activated handler does — so checking focus *inside* the handler is too
        late to help; unlike QLineEdit, QComboBox doesn't reserve its own
        arrow-key/type-ahead keys via ShortcutOverride, so leaving these
        shortcuts enabled breaks the combo box's own keyboard handling
        entirely. Wired to QApplication.focusChanged so it stays correct as
        focus moves around, not just at the moment each shortcut fires."""
        active = not isinstance(new, QComboBox)
        for shortcut in self._combo_sensitive_shortcuts:
            shortcut.setEnabled(active)

    def _cycle_source(self, direction: int):
        """Select the next/previous combatant (direction +1/-1) as source,
        cycling through self.characters and wrapping around."""
        if not self.characters:
            return
        idx = next(
            (i for i, c in enumerate(self.characters) if c is self.selected_character),
            -1,
        )
        new_idx = (idx + direction) % len(self.characters)
        self._select_character(self.characters[new_idx])

    def _cycle_target(self, direction: int):
        """Select the next/previous combatant (direction +1/-1) as the sole
        target, cycling through self.characters and wrapping around."""
        if not self.characters:
            return
        current = self.target_characters[0] if self.target_characters else None
        idx = next((i for i, c in enumerate(self.characters) if c is current), -1)
        new_idx = (idx + direction) % len(self.characters)
        self._select_target_character(self.characters[new_idx], additive=False)

    def _shortcut_select_active_source(self):
        """Keyboard shortcut 'Space': select whoever's turn it currently is as
        the source, saving a mouse click at the start of every turn."""
        if self.phase != "COMBAT" or not self.initiative_order:
            return
        self._select_character(self.initiative_order[self.current_turn_idx])

    def _focus_damage_input(self):
        self.damage_input.setFocus()
        self.damage_input.selectAll()

    def _focus_heal_input(self):
        self.heal_input.setFocus()
        self.heal_input.selectAll()

    def _focus_temp_hp_input(self):
        self.temp_hp_input.setFocus()
        self.temp_hp_input.selectAll()

    def _build_window(self):
        self._window = QMainWindow()
        self._window.setWindowTitle("DnD Combat Engine")
        self._window.setMinimumSize(900, 600)
        self._window.resize(2400, 1300)

        central = QWidget()
        self._window.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # --- Left: scrollable area (initiative or card grid) ---
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Build the card grid container (hidden until combat starts)
        self._cards_container = QWidget()
        self._grid_layout = QGridLayout(self._cards_container)
        self._grid_layout.setSpacing(8)
        self._grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self._cards_container.hide()

        # Build and show the initiative widget
        self._initiative_widget = self._build_initiative_widget()
        self._scroll_area.setWidget(self._initiative_widget)

        root_layout.addWidget(self._scroll_area, stretch=1)

        # --- Right: control panel ---
        panel = QFrame()
        panel.setObjectName("controlPanel")
        panel.setFixedWidth(460)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(6)

        # Selected indicator (source — left-click)
        self.selected_label = QLabel("Source: None")
        self.selected_label.setObjectName("selectedLabel")
        self.selected_label.setWordWrap(True)
        panel_layout.addWidget(self.selected_label)

        # Target indicator (right-click)
        self.target_label = QLabel("Target: None")
        self.target_label.setObjectName("targetLabel")
        self.target_label.setWordWrap(True)
        panel_layout.addWidget(self.target_label)

        info_cast_row = QHBoxLayout()
        info_cast_row.setSpacing(6)
        self._more_info_btn = QPushButton("More Info")
        self._more_info_btn.setEnabled(False)
        self._more_info_btn.clicked.connect(self._show_more_info)
        info_cast_row.addWidget(self._more_info_btn)

        self._cast_spell_btn = QPushButton("Cast Spell")
        self._cast_spell_btn.setEnabled(False)
        self._cast_spell_btn.clicked.connect(self._show_cast_spell_dialog)
        info_cast_row.addWidget(self._cast_spell_btn)
        panel_layout.addLayout(info_cast_row)

        # Round indicator + session/player timers (compact, combined rows)
        panel_layout.addWidget(self._build_timer_section())
        panel_layout.addWidget(self._make_divider())

        # Initiative tracker container (hidden during initiative phase, shown during combat)
        self._init_tracker_container = QWidget()
        self._init_tracker_container.hide()
        tracker_outer = QVBoxLayout(self._init_tracker_container)
        tracker_outer.setContentsMargins(0, 0, 0, 0)
        tracker_outer.setSpacing(2)

        self._turn_counter_label = QLabel("Turn 1 / 1")
        self._turn_counter_label.setStyleSheet(
            "color: #c9a84c; font-weight: bold; font-size: 11px;"
        )
        tracker_outer.addWidget(self._turn_counter_label)

        panel_layout.addWidget(self._init_tracker_container)

        panel_layout.addWidget(self._make_divider())

        # Two-column layout for controls
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(6)

        # Left column: Damage, Heal, Temp HP
        left_col = QVBoxLayout()
        left_col.setSpacing(6)

        # Damage section
        left_col.addWidget(self._section_header("Damage"))
        dmg_input_row = QHBoxLayout()
        dmg_input_row.setSpacing(4)
        self.damage_input = QLineEdit()
        self.damage_input.setPlaceholderText("Amount...")
        self.damage_input.returnPressed.connect(self._apply_damage)
        dmg_input_row.addWidget(self.damage_input, stretch=2)

        self.damage_type_combo = QComboBox()
        self.damage_type_combo.addItem("— Type —", None)
        for dtype in DamageType:
            self.damage_type_combo.addItem(dtype.value, dtype.value)
            self.damage_type_combo.setItemData(
                self.damage_type_combo.count() - 1,
                QColor(get_damage_type_color(dtype.value)),
                Qt.ItemDataRole.ForegroundRole,
            )

        def _update_damage_type_combo_color():
            dtype_value = self.damage_type_combo.currentData()
            color = get_damage_type_color(dtype_value) if dtype_value else "#eaeaea"
            self.damage_type_combo.setStyleSheet(
                f"QComboBox {{ color: {color}; font-weight: bold; }}"
            )

        self.damage_type_combo.currentIndexChanged.connect(
            lambda _index: _update_damage_type_combo_color()
        )
        _update_damage_type_combo_color()

        dmg_input_row.addWidget(self.damage_type_combo, stretch=3)
        left_col.addLayout(dmg_input_row)

        dmg_btn_row = QHBoxLayout()
        dmg_btn_row.setSpacing(4)
        dmg_btn = QPushButton("Apply")
        dmg_btn.setObjectName("primaryBtn")
        dmg_btn.clicked.connect(self._apply_damage)
        dmg_btn_row.addWidget(dmg_btn)

        dmg_checked_btn = QPushButton("Apply (Check Resist)")
        dmg_checked_btn.clicked.connect(self._apply_damage_checked)
        dmg_btn_row.addWidget(dmg_checked_btn)
        left_col.addLayout(dmg_btn_row)

        left_col.addWidget(self._make_divider())

        # Heal section
        left_col.addWidget(self._section_header("Heal"))
        self.heal_input = QLineEdit()
        self.heal_input.setPlaceholderText("Amount...")
        self.heal_input.setStyleSheet(
            "QLineEdit { background-color: #0f3460; border: 1px solid #4caf82; "
            "border-radius: 3px; color: #eaeaea; padding: 3px 5px; }"
            "QLineEdit:focus { border: 1px solid #5cdf92; }"
        )
        left_col.addWidget(self.heal_input)
        self.heal_input.returnPressed.connect(self._apply_heal)
        heal_btn = QPushButton("Apply Heal")
        heal_btn.setObjectName("healBtn")
        heal_btn.clicked.connect(self._apply_heal)
        left_col.addWidget(heal_btn)

        left_col.addWidget(self._make_divider())

        # Temp HP section
        left_col.addWidget(self._section_header("Temp HP"))
        self.temp_hp_input = QLineEdit()
        self.temp_hp_input.setPlaceholderText("Amount...")
        self.temp_hp_input.setStyleSheet(
            "QLineEdit { background-color: #0f3460; border: 1px solid #4a9fc4; "
            "border-radius: 3px; color: #eaeaea; padding: 3px 5px; }"
            "QLineEdit:focus { border: 1px solid #5ac8f5; }"
        )
        left_col.addWidget(self.temp_hp_input)
        self.temp_hp_input.returnPressed.connect(self._apply_temp_hp)
        temp_hp_btn = QPushButton("Add Temp HP")
        temp_hp_btn.setObjectName("tempHpBtn")
        temp_hp_btn.clicked.connect(self._apply_temp_hp)
        left_col.addWidget(temp_hp_btn)

        left_col.addWidget(self._make_divider())

        # d20 roll section (advantage / neutral / disadvantage)
        left_col.addWidget(self._section_header("d20 Roll"))
        roll_row = QHBoxLayout()
        roll_row.setSpacing(4)
        self.roll_mode_combo = QComboBox()
        self.roll_mode_combo.addItems(["Neutral", "Advantage", "Disadvantage"])
        roll_row.addWidget(self.roll_mode_combo, stretch=2)
        roll_btn = QPushButton("Roll")
        roll_btn.clicked.connect(self._roll_d20)
        roll_row.addWidget(roll_btn, stretch=1)
        left_col.addLayout(roll_row)

        self.roll_result_label = QLabel("")
        self.roll_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.roll_result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_col.addWidget(self.roll_result_label)

        left_col.addStretch()

        # Right column: Conditions, Visibility, Spell Slots
        right_col = QVBoxLayout()
        right_col.setSpacing(6)

        # Conditions section
        right_col.addWidget(self._section_header("Conditions"))
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(self.conditions)
        right_col.addWidget(self.condition_combo)
        cond_row = QHBoxLayout()
        add_cond_btn = QPushButton("Add")
        add_cond_btn.clicked.connect(self._add_condition)
        rm_cond_btn = QPushButton("Remove")
        rm_cond_btn.clicked.connect(self._remove_condition)
        cond_row.addWidget(add_cond_btn)
        cond_row.addWidget(rm_cond_btn)
        right_col.addLayout(cond_row)

        right_col.addWidget(self._make_divider())

        # Visibility section
        right_col.addWidget(self._section_header("Visibility"))
        self.visibility_combo = QComboBox()
        self.visibility_combo.addItems(self.visibility_states)
        right_col.addWidget(self.visibility_combo)
        vis_row = QHBoxLayout()
        add_vis_btn = QPushButton("Add")
        add_vis_btn.clicked.connect(self._add_visibility)
        rm_vis_btn = QPushButton("Remove")
        rm_vis_btn.clicked.connect(self._remove_visibility)
        vis_row.addWidget(add_vis_btn)
        vis_row.addWidget(rm_vis_btn)
        right_col.addLayout(vis_row)

        right_col.addWidget(self._make_divider())

        # Spell slots section
        right_col.addWidget(self._section_header("Spell Slots"))
        self.spell_combo = QComboBox()
        self.spell_combo.addItems([f"Level {i}" for i in range(1, 10)])
        right_col.addWidget(self.spell_combo)
        spell_row = QHBoxLayout()
        cast_btn = QPushButton("Cast (1-9)")
        cast_btn.clicked.connect(
            lambda: self._cast_spell_slot_level(self.spell_combo.currentIndex() + 1)
        )
        regain_btn = QPushButton("Regain")
        regain_btn.clicked.connect(self._regain_spell_slot)
        spell_row.addWidget(cast_btn)
        spell_row.addWidget(regain_btn)
        right_col.addLayout(spell_row)

        right_col.addWidget(self._make_divider())

        # Action economy section (resets on this combatant's next turn)
        right_col.addWidget(self._section_header("Action Economy"))
        self.action_economy_combo = QComboBox()
        self.action_economy_combo.addItems(self.ACTION_ECONOMY_TYPES)
        right_col.addWidget(self.action_economy_combo)
        action_economy_row = QHBoxLayout()
        add_action_btn = QPushButton("Add (A/B/R)")
        add_action_btn.clicked.connect(
            lambda: self._add_action_use(self.action_economy_combo.currentText())
        )
        rm_action_btn = QPushButton("Remove")
        rm_action_btn.clicked.connect(
            lambda: self._remove_action_use(self.action_economy_combo.currentText())
        )
        action_economy_row.addWidget(add_action_btn)
        action_economy_row.addWidget(rm_action_btn)
        right_col.addLayout(action_economy_row)

        right_col.addStretch()

        # Add both columns to the columns layout
        columns_layout.addLayout(left_col)
        columns_layout.addLayout(right_col)

        # Add columns to main panel layout
        panel_layout.addLayout(columns_layout)

        panel_layout.addWidget(self._make_divider())

        # Actions section
        panel_layout.addWidget(self._section_header("Actions"))

        add_combatant_btn = QPushButton("+ Add Combatant")
        add_combatant_btn.clicked.connect(self._show_add_combatant_dialog)
        panel_layout.addWidget(add_combatant_btn)

        # Next turn button (hidden during initiative phase)
        self._turn_divider = self._make_divider()
        self._turn_divider.hide()
        panel_layout.addWidget(self._turn_divider)

        self._next_turn_btn = QPushButton("Next Combatant")
        self._next_turn_btn.clicked.connect(self._advance_turn)
        self._next_turn_btn.hide()
        self._next_turn_btn.setStyleSheet(
            "background-color: #3a2e00; border: 1px solid #c9a84c;"
            " color: #c9a84c; font-weight: bold; min-height: 28px;"
        )
        panel_layout.addWidget(self._next_turn_btn)

        undo_btn = QPushButton("Undo Last Action")
        undo_btn.clicked.connect(self._undo_last)
        panel_layout.addWidget(undo_btn)

        log_status_label = QLabel(self._log_status_text())
        log_status_label.setWordWrap(True)
        log_status_label.setStyleSheet("color: #a0a0b0; font-size: 11px;")
        panel_layout.addWidget(log_status_label)

        log_btn = QPushButton("Encounter Log")
        log_btn.clicked.connect(self._show_current_log)
        panel_layout.addWidget(log_btn)

        player_log_btn = QPushButton("Player Log")
        player_log_btn.clicked.connect(self._show_player_log)
        panel_layout.addWidget(player_log_btn)

        stats_btn = QPushButton("Statistics")
        stats_btn.clicked.connect(self._show_statistics)
        panel_layout.addWidget(stats_btn)

        rules_btn = QPushButton("Rules")
        rules_btn.clicked.connect(self._show_rules)
        panel_layout.addWidget(rules_btn)

        panel_layout.addStretch()
        root_layout.addWidget(panel)

        # Shortcuts that must stand down (fully disabled, not just a no-op
        # handler) while a combo box has focus — see _update_combo_sensitive_shortcuts.
        self._combo_sensitive_shortcuts: list[QShortcut] = []

        # Keyboard shortcuts: A / B / R log an Action / Bonus Action / Reaction use
        # for the current source. These naturally yield to any focused text field.
        self._action_shortcuts = []
        for key, action_type in self.ACTION_ECONOMY_SHORTCUTS.items():
            shortcut = QShortcut(QKeySequence(key), self._window)
            shortcut.activated.connect(lambda a=action_type: self._add_action_use(a))
            self._action_shortcuts.append(shortcut)
        self._combo_sensitive_shortcuts += self._action_shortcuts

        # C / Ctrl+C / Ctrl+Shift+C: Concentrating on the source, cleared from the target.
        self._concentration_shortcut = QShortcut(QKeySequence("C"), self._window)
        self._concentration_shortcut.activated.connect(self._shortcut_add_concentration)
        self._remove_concentration_shortcut = QShortcut(QKeySequence("Ctrl+C"), self._window)
        self._remove_concentration_shortcut.activated.connect(self._shortcut_remove_concentration)
        self._clear_target_conditions_shortcut = QShortcut(
            QKeySequence("Ctrl+Shift+C"), self._window
        )
        self._clear_target_conditions_shortcut.activated.connect(
            self._shortcut_clear_target_conditions
        )
        self._combo_sensitive_shortcuts += [
            self._concentration_shortcut,
            self._remove_concentration_shortcut,
            self._clear_target_conditions_shortcut,
        ]

        # Ctrl+Z: Undo Last Action
        self._undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self._window)
        self._undo_shortcut.activated.connect(self._undo_last)

        # Escape: clear source and target selection
        self._clear_selection_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self._window)
        self._clear_selection_shortcut.activated.connect(self._clear_selection)

        # Enter / Return: Next Combatant / Next Round
        self._next_turn_shortcuts = [
            QShortcut(QKeySequence(Qt.Key.Key_Return), self._window),
            QShortcut(QKeySequence(Qt.Key.Key_Enter), self._window),
        ]
        for shortcut in self._next_turn_shortcuts:
            shortcut.activated.connect(self._shortcut_next_turn)

        # 1-9: cast a spell slot of that level for the source
        self._spell_slot_shortcuts = []
        for level in range(1, 10):
            shortcut = QShortcut(QKeySequence(str(level)), self._window)
            shortcut.activated.connect(lambda lvl=level: self._cast_spell_slot_level(lvl))
            self._spell_slot_shortcuts.append(shortcut)
        self._combo_sensitive_shortcuts += self._spell_slot_shortcuts

        # N / P (and Left / Right arrow aliases): select next / previous
        # combatant as source. Shift+N / Shift+P (and Up / Down arrow
        # aliases): same, as target. A focused text field keeps its own
        # cursor-movement arrow keys regardless (see the class docstring above).
        self._cycle_source_next_shortcut = QShortcut(QKeySequence("N"), self._window)
        self._cycle_source_next_shortcut.activated.connect(lambda: self._cycle_source(1))
        self._cycle_source_prev_shortcut = QShortcut(QKeySequence("P"), self._window)
        self._cycle_source_prev_shortcut.activated.connect(lambda: self._cycle_source(-1))
        self._cycle_target_next_shortcut = QShortcut(QKeySequence("Shift+N"), self._window)
        self._cycle_target_next_shortcut.activated.connect(lambda: self._cycle_target(1))
        self._cycle_target_prev_shortcut = QShortcut(QKeySequence("Shift+P"), self._window)
        self._cycle_target_prev_shortcut.activated.connect(lambda: self._cycle_target(-1))

        self._cycle_source_right_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self._window)
        self._cycle_source_right_shortcut.activated.connect(lambda: self._cycle_source(1))
        self._cycle_source_left_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self._window)
        self._cycle_source_left_shortcut.activated.connect(lambda: self._cycle_source(-1))
        self._cycle_target_down_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Down), self._window)
        self._cycle_target_down_shortcut.activated.connect(lambda: self._cycle_target(1))
        self._cycle_target_up_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Up), self._window)
        self._cycle_target_up_shortcut.activated.connect(lambda: self._cycle_target(-1))
        self._combo_sensitive_shortcuts += [
            self._cycle_source_next_shortcut,
            self._cycle_source_prev_shortcut,
            self._cycle_target_next_shortcut,
            self._cycle_target_prev_shortcut,
            self._cycle_source_right_shortcut,
            self._cycle_source_left_shortcut,
            self._cycle_target_down_shortcut,
            self._cycle_target_up_shortcut,
        ]

        # Space: select whoever's turn it is as the source
        self._select_active_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self._window)
        self._select_active_shortcut.activated.connect(self._shortcut_select_active_source)
        self._combo_sensitive_shortcuts.append(self._select_active_shortcut)

        # D / H / T: jump straight into the Damage / Heal / Temp HP amount field
        self._focus_damage_shortcut = QShortcut(QKeySequence("D"), self._window)
        self._focus_damage_shortcut.activated.connect(self._focus_damage_input)
        self._focus_heal_shortcut = QShortcut(QKeySequence("H"), self._window)
        self._focus_heal_shortcut.activated.connect(self._focus_heal_input)
        self._focus_temp_hp_shortcut = QShortcut(QKeySequence("T"), self._window)
        self._focus_temp_hp_shortcut.activated.connect(self._focus_temp_hp_input)
        self._combo_sensitive_shortcuts += [
            self._focus_damage_shortcut,
            self._focus_heal_shortcut,
            self._focus_temp_hp_shortcut,
        ]

        # Ctrl+N: open the Add Combatant dialog
        self._add_combatant_shortcut = QShortcut(QKeySequence("Ctrl+N"), self._window)
        self._add_combatant_shortcut.activated.connect(self._show_add_combatant_dialog)
        self._combo_sensitive_shortcuts.append(self._add_combatant_shortcut)

        # Keep the shortcuts above disabled while focus is on a combo box, and
        # restored the instant it moves elsewhere (see the method docstring).
        QApplication.instance().focusChanged.connect(self._update_combo_sensitive_shortcuts)
        self._update_combo_sensitive_shortcuts(None, QApplication.focusWidget())

    @staticmethod
    def _make_divider() -> QFrame:
        line = QFrame()
        line.setObjectName("divider")
        line.setFrameShape(QFrame.Shape.HLine)
        return line

    @staticmethod
    def _section_header(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionHeader")
        return lbl
