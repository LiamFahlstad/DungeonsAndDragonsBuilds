"""Window/UI construction mixin for CombatAppQt."""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
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

from .styles import QSS


class WindowMixin:
    """Mixin for window building and selection logic."""

    def _select_character(self, char: dict):
        self.selected_character = char
        self.selected_label.setText(f"Source: {char['name']}")
        self._more_info_btn.setEnabled(True)
        self._cast_spell_btn.setEnabled(True)
        self._refresh_cards()

    def _select_target_character(self, char: dict):
        self.target_character = char
        self.target_label.setText(f"Target: {char['name']}")
        self._refresh_cards()

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

        self._more_info_btn = QPushButton("More Info")
        self._more_info_btn.setEnabled(False)
        self._more_info_btn.clicked.connect(self._show_more_info)
        panel_layout.addWidget(self._more_info_btn)

        self._cast_spell_btn = QPushButton("Cast Spell")
        self._cast_spell_btn.setEnabled(False)
        self._cast_spell_btn.clicked.connect(self._show_cast_spell_dialog)
        panel_layout.addWidget(self._cast_spell_btn)

        # Round indicator
        self.round_label = QLabel(f"Round {self.round_number}")
        self.round_label.setStyleSheet(
            "color: #c9a84c; font-weight: bold; font-size: 12px;"
        )
        panel_layout.addWidget(self.round_label)

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
        self.damage_input = QLineEdit()
        self.damage_input.setPlaceholderText("Amount...")
        left_col.addWidget(self.damage_input)
        self.damage_input.returnPressed.connect(self._apply_damage)
        dmg_btn = QPushButton("Apply Damage")
        dmg_btn.setObjectName("primaryBtn")
        dmg_btn.clicked.connect(self._apply_damage)
        left_col.addWidget(dmg_btn)

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

        log_btn = QPushButton("Open Current Log")
        log_btn.clicked.connect(self._show_current_log)
        panel_layout.addWidget(log_btn)

        stats_btn = QPushButton("Statistics")
        stats_btn.clicked.connect(self._show_statistics)
        panel_layout.addWidget(stats_btn)

        rules_btn = QPushButton("Rules")
        rules_btn.clicked.connect(self._show_rules)
        panel_layout.addWidget(rules_btn)

        panel_layout.addStretch()
        root_layout.addWidget(panel)

        # Keyboard shortcuts: A / B / R log an Action / Bonus Action / Reaction use
        # for the current source. These naturally yield to any focused text field.
        self._action_shortcuts = []
        for key, action_type in self.ACTION_ECONOMY_SHORTCUTS.items():
            shortcut = QShortcut(QKeySequence(key), self._window)
            shortcut.activated.connect(lambda a=action_type: self._add_action_use(a))
            self._action_shortcuts.append(shortcut)

        # C / Ctrl+C / Ctrl+Shift+C: Concentrating on the source, cleared from the target.
        self._concentration_shortcut = QShortcut(QKeySequence("C"), self._window)
        self._concentration_shortcut.activated.connect(self._shortcut_add_concentration)
        self._remove_concentration_shortcut = QShortcut(QKeySequence("Ctrl+C"), self._window)
        self._remove_concentration_shortcut.activated.connect(
            self._shortcut_remove_concentration
        )
        self._clear_target_conditions_shortcut = QShortcut(
            QKeySequence("Ctrl+Shift+C"), self._window
        )
        self._clear_target_conditions_shortcut.activated.connect(
            self._shortcut_clear_target_conditions
        )

        # Ctrl+Z: Undo Last Action
        self._undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self._window)
        self._undo_shortcut.activated.connect(self._undo_last)

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
