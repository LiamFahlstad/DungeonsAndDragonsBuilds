import json
import sys
from datetime import datetime
from pathlib import Path

import CharacterSheetCreator
import Definitions
from Combat.Definitions import Action, BasicCombatantData, Condition
from Features import Armor

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

# ---------------------------------------------------------------------------
# Global stylesheet — dark fantasy theme
# ---------------------------------------------------------------------------
QSS = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}

/* Combatant cards */
QFrame#combatantCard {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
}
QFrame#combatantCard[selected="true"] {
    background-color: #1e2d5a;
    border: 2px solid #e94560;
}

/* Control panel */
QFrame#controlPanel {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
}

/* Dividers */
QFrame#divider {
    background-color: #0f3460;
    max-height: 1px;
    min-height: 1px;
}

/* Section headers inside control panel */
QLabel#sectionHeader {
    color: #c9a84c;
    font-weight: bold;
    font-size: 11px;
}

/* Card name label */
QLabel#cardName {
    color: #c9a84c;
    font-weight: bold;
    font-size: 13px;
}

/* Secondary text */
QLabel#secondary {
    color: #a0a0b0;
    font-size: 11px;
}

/* Condition badge */
QLabel#conditionBadge {
    background-color: #7a5c00;
    color: #ffffff;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: 10px;
}

/* Selected combatant label */
QLabel#selectedLabel {
    color: #e94560;
    font-weight: bold;
    font-size: 12px;
}

/* HP bar */
QProgressBar {
    border: 1px solid #0f3460;
    border-radius: 3px;
    background-color: #555;
    text-align: center;
    color: #eaeaea;
    font-size: 10px;
    min-height: 14px;
    max-height: 14px;
}
QProgressBar::chunk#hp_green  { background-color: #2ecc71; border-radius: 3px; }
QProgressBar::chunk#hp_orange { background-color: #e67e22; border-radius: 3px; }
QProgressBar::chunk#hp_red    { background-color: #e74c3c; border-radius: 3px; }
QProgressBar::chunk#hp_dead   { background-color: #555;    border-radius: 3px; }

/* Inputs */
QLineEdit {
    background-color: #0f3460;
    border: 1px solid #e94560;
    border-radius: 3px;
    color: #eaeaea;
    padding: 3px 5px;
}
QLineEdit:focus {
    border: 1px solid #c9a84c;
}

QComboBox {
    background-color: #0f3460;
    border: 1px solid #0f3460;
    border-radius: 3px;
    color: #eaeaea;
    padding: 2px 5px;
}
QComboBox::drop-down {
    border: none;
    width: 16px;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #eaeaea;
    selection-background-color: #0f3460;
}

/* Buttons — base */
QPushButton {
    background-color: #0f3460;
    color: #eaeaea;
    border: 1px solid #1a4a80;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #1a4a80;
}
QPushButton:pressed {
    background-color: #0a2540;
}

/* Primary buttons (damage / heal) */
QPushButton#primaryBtn {
    background-color: #3d1a2e;
    border: 1px solid #e94560;
    color: #e94560;
    font-weight: bold;
}
QPushButton#primaryBtn:hover {
    background-color: #5a2040;
}
QPushButton#primaryBtn:pressed {
    background-color: #2a0f1e;
}

/* Scrollbar styling */
QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 0; }
"""


# ---------------------------------------------------------------------------
# CombatAppQt
# ---------------------------------------------------------------------------
class CombatAppQt:
    def __init__(
        self,
        combatants: list[BasicCombatantData],
        character_sheets: list,
        combatants_per_column: int = 4,
    ):
        self.combatants_per_column = combatants_per_column

        # ---- data ----
        self.characters: list[dict] = []
        for cs in character_sheets:
            self._add_from_character_sheet(cs)
        for c in combatants:
            self._add_basic_combatant(c)

        self.conditions = Condition.list_all()
        self.selected_character: dict | None = None
        self.round_number = 1
        self.history: list[tuple[Action, str | int | tuple[int, int]]] = []

        log_dir = Path("CombatLogs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = log_dir / f"combat_log_{timestamp}.json"
        self._write_log({})

        # card widget registry: maps id(char_dict) -> QFrame
        self._card_widgets: dict[int, QFrame] = {}

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def _add_from_character_sheet(self, character_sheet):
        character = character_sheet.setup_character_stat_block()
        ac = character.calculate_armor_class()
        if Armor.ShieldArmor in [type(a) for a in character_sheet.armors]:
            ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"
        else:
            ac = f"{ac} (no Shield)"
        try:
            spell_slots = character.get_spell_slots()
        except ValueError:
            spell_slots = {}
        hp = character.calculate_hit_points()
        self.characters.append(
            {
                "name": character_sheet.character_name,
                "hp": hp,
                "max_hp": hp,
                "ac": ac,
                "temp_hp": 0,
                "conditions": [],
                "spell_slots": spell_slots,
                "Ability Scores": {
                    ability.name: character.get_ability_score(ability)
                    for ability in Definitions.Ability
                },
                "Saving Throws": {
                    ability.name: character.get_saving_throw_modifier(ability)
                    for ability in Definitions.Ability
                },
            }
        )

    def _add_basic_combatant(self, combatant: BasicCombatantData):
        self.characters.append(
            {
                "name": combatant.name,
                "hp": combatant.hp,
                "max_hp": combatant.max_hp,
                "ac": combatant.ac,
                "temp_hp": combatant.temp_hp,
                "conditions": [cond.value for cond in combatant.conditions],
                "spell_slots": combatant.spell_slots,
                "Ability Scores": combatant.ability_scores,
                "Saving Throws": combatant.saving_throws,
            }
        )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def _write_log(self, data: dict):
        data["round_number"] = self.round_number
        data["combatants"] = [dict(c) for c in self.characters]
        self.log_file.write_text(json.dumps(data, indent=2))

    def _log_event(self, text: str):
        data = json.loads(self.log_file.read_text())
        key = f"round_{self.round_number}"
        data.setdefault(key, []).append(text)
        self._write_log(data)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _select_character(self, char: dict):
        self.selected_character = char
        self.selected_label.setText(f"Selected: {char['name']}")
        self._refresh_cards()

    def _apply_damage(self):
        if not self.selected_character:
            return
        try:
            dmg = int(self.damage_input.text())
        except ValueError:
            return

        pre_hp = self.selected_character["hp"]
        pre_temp = self.selected_character["temp_hp"]

        temp_reduction = min(self.selected_character["temp_hp"], dmg)
        self.selected_character["temp_hp"] -= temp_reduction
        self.selected_character["hp"] -= dmg - temp_reduction

        hp_delta = self.selected_character["hp"] - pre_hp
        temp_delta = self.selected_character["temp_hp"] - pre_temp
        self.history.append((Action.DAMAGE, (hp_delta, temp_delta)))
        self._log_event(f"{self.selected_character['name']} takes {dmg} damage")
        self._refresh_selected_card()

    def _apply_heal(self):
        if not self.selected_character:
            return
        try:
            heal = int(self.heal_input.text())
        except ValueError:
            return

        self.selected_character["hp"] = min(
            self.selected_character["hp"] + heal,
            self.selected_character["max_hp"],
        )
        self.history.append((Action.HEAL, heal))
        self._log_event(f"{self.selected_character['name']} heals {heal} HP")
        self._refresh_selected_card()

    def _add_condition(self):
        if not self.selected_character:
            return
        cond = self.condition_combo.currentText()
        if cond not in self.selected_character["conditions"]:
            self.selected_character["conditions"].append(cond)
            self.history.append((Action.ADD_CONDITION, cond))
            self._log_event(f"{self.selected_character['name']} gains {cond}")
            self._refresh_selected_card()

    def _remove_condition(self):
        if not self.selected_character:
            return
        cond = self.condition_combo.currentText()
        if cond in self.selected_character["conditions"]:
            self.selected_character["conditions"].remove(cond)
            self.history.append((Action.REMOVE_CONDITION, cond))
            self._log_event(f"{self.selected_character['name']} loses {cond}")
            self._refresh_selected_card()

    def _cast_spell_slot(self):
        if not self.selected_character:
            return
        level = self.spell_combo.currentIndex() + 1
        if self.selected_character["spell_slots"].get(level, 0) <= 0:
            return
        old = self.selected_character["spell_slots"][level]
        self.selected_character["spell_slots"][level] = max(old - 1, 0)
        self.history.append((Action.REMOVE_SPELL_SLOT, level))
        self._log_event(
            f"{self.selected_character['name']} uses a Level {level} spell slot"
        )
        self._refresh_selected_card()

    def _regain_spell_slot(self):
        if not self.selected_character:
            return
        level = self.spell_combo.currentIndex() + 1
        old = self.selected_character["spell_slots"].get(level, 0)
        self.selected_character["spell_slots"][level] = old + 1
        self.history.append((Action.ADD_SPELL_SLOT, level))
        self._log_event(
            f"{self.selected_character['name']} regains a Level {level} spell slot"
        )
        self._refresh_selected_card()

    def _undo_last(self):
        if not self.selected_character or not self.history:
            return
        data = json.loads(self.log_file.read_text())
        key = f"round_{self.round_number}"
        if key not in data or not data[key]:
            return

        action, value = self.history.pop()
        char = self.selected_character

        if action == Action.DAMAGE:
            if isinstance(value, tuple):
                hp_delta, temp_delta = value
                char["hp"] -= hp_delta
                char["temp_hp"] -= temp_delta
            else:
                char["hp"] += value
        elif action == Action.HEAL:
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
            char["spell_slots"][value] = max(
                char["spell_slots"].get(value, 0) - 1, 0
            )

        last_event = data[key].pop()
        self._write_log(data)
        print(f"Undid action: {last_event}")
        self._refresh_selected_card()

    def _next_round(self):
        self.round_number += 1
        self._log_event(f"--- Round {self.round_number} ---")
        self.round_label.setText(f"Round {self.round_number}")

    def _load_log(self):
        path, _ = QFileDialog.getOpenFileName(
            self._window,
            "Load Combat Log",
            str(Path("CombatLogs").resolve()),
            "JSON files (*.json)",
        )
        if not path:
            return
        data = json.loads(Path(path).read_text())
        if "combatants" not in data:
            QMessageBox.warning(self._window, "Error", "No combatants key in log file.")
            return
        self.characters = data["combatants"]
        self.round_number = data.get("round_number", 1)
        self.history = []
        self.selected_character = None
        self.selected_label.setText("Selected: None")
        self.round_label.setText(f"Round {self.round_number}")
        self.log_file = Path(path)
        self._rebuild_cards()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_window(self):
        self._window = QMainWindow()
        self._window.setWindowTitle("DnD Combat Engine")
        self._window.setMinimumSize(900, 600)

        central = QWidget()
        self._window.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # --- Left: scrollable card grid ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._cards_container = QWidget()
        self._grid_layout = QGridLayout(self._cards_container)
        self._grid_layout.setSpacing(8)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self._cards_container)
        root_layout.addWidget(scroll, stretch=1)

        # --- Right: control panel ---
        panel = QFrame()
        panel.setObjectName("controlPanel")
        panel.setFixedWidth(230)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(6)

        # Selected indicator
        self.selected_label = QLabel("Selected: None")
        self.selected_label.setObjectName("selectedLabel")
        self.selected_label.setWordWrap(True)
        panel_layout.addWidget(self.selected_label)

        # Round indicator
        self.round_label = QLabel(f"Round {self.round_number}")
        self.round_label.setStyleSheet("color: #c9a84c; font-weight: bold; font-size: 12px;")
        panel_layout.addWidget(self.round_label)

        panel_layout.addWidget(self._make_divider())

        # Damage section
        panel_layout.addWidget(self._section_header("Damage"))
        self.damage_input = QLineEdit()
        self.damage_input.setPlaceholderText("Amount...")
        panel_layout.addWidget(self.damage_input)
        dmg_btn = QPushButton("Apply Damage")
        dmg_btn.setObjectName("primaryBtn")
        dmg_btn.clicked.connect(self._apply_damage)
        panel_layout.addWidget(dmg_btn)

        panel_layout.addWidget(self._make_divider())

        # Heal section
        panel_layout.addWidget(self._section_header("Heal"))
        self.heal_input = QLineEdit()
        self.heal_input.setPlaceholderText("Amount...")
        panel_layout.addWidget(self.heal_input)
        heal_btn = QPushButton("Apply Heal")
        heal_btn.setObjectName("primaryBtn")
        heal_btn.clicked.connect(self._apply_heal)
        panel_layout.addWidget(heal_btn)

        panel_layout.addWidget(self._make_divider())

        # Conditions section
        panel_layout.addWidget(self._section_header("Conditions"))
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(self.conditions)
        panel_layout.addWidget(self.condition_combo)
        cond_row = QHBoxLayout()
        add_cond_btn = QPushButton("Add")
        add_cond_btn.clicked.connect(self._add_condition)
        rm_cond_btn = QPushButton("Remove")
        rm_cond_btn.clicked.connect(self._remove_condition)
        cond_row.addWidget(add_cond_btn)
        cond_row.addWidget(rm_cond_btn)
        panel_layout.addLayout(cond_row)

        panel_layout.addWidget(self._make_divider())

        # Spell slots section
        panel_layout.addWidget(self._section_header("Spell Slots"))
        self.spell_combo = QComboBox()
        self.spell_combo.addItems([f"Level {i}" for i in range(1, 10)])
        panel_layout.addWidget(self.spell_combo)
        spell_row = QHBoxLayout()
        cast_btn = QPushButton("Cast")
        cast_btn.clicked.connect(self._cast_spell_slot)
        regain_btn = QPushButton("Regain")
        regain_btn.clicked.connect(self._regain_spell_slot)
        spell_row.addWidget(cast_btn)
        spell_row.addWidget(regain_btn)
        panel_layout.addLayout(spell_row)

        panel_layout.addWidget(self._make_divider())

        # Actions section
        panel_layout.addWidget(self._section_header("Actions"))
        undo_btn = QPushButton("Undo Last Action")
        undo_btn.clicked.connect(self._undo_last)
        panel_layout.addWidget(undo_btn)

        next_btn = QPushButton("Next Round")
        next_btn.clicked.connect(self._next_round)
        panel_layout.addWidget(next_btn)

        load_btn = QPushButton("Load Combat Log")
        load_btn.clicked.connect(self._load_log)
        panel_layout.addWidget(load_btn)

        panel_layout.addStretch()
        root_layout.addWidget(panel)

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

    # ------------------------------------------------------------------
    # Card rendering
    # ------------------------------------------------------------------
    def _rebuild_cards(self):
        """Remove all card widgets and recreate them from self.characters."""
        # Clear existing cards
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._card_widgets.clear()

        for index, char in enumerate(self.characters):
            col = index // self.combatants_per_column
            row = index % self.combatants_per_column
            card = self._make_card(char)
            self._grid_layout.addWidget(card, row, col)
            self._card_widgets[id(char)] = card

    def _refresh_cards(self):
        """Update border/background of all cards to reflect selection state."""
        for char in self.characters:
            card = self._card_widgets.get(id(char))
            if card is None:
                continue
            is_selected = char is self.selected_character
            card.setProperty("selected", "true" if is_selected else "false")
            card.style().unpolish(card)
            card.style().polish(card)

    def _refresh_selected_card(self):
        """Rebuild only the selected card in-place (after stat changes)."""
        if self.selected_character is None:
            return
        char = self.selected_character
        card_id = id(char)
        old_card = self._card_widgets.get(card_id)
        if old_card is None:
            return

        # Find its position in the grid
        idx = self._grid_layout.indexOf(old_card)
        if idx < 0:
            return
        pos = self._grid_layout.getItemPosition(idx)  # (row, col, rowSpan, colSpan)
        grid_row, grid_col = pos[0], pos[1]

        # Remove old card
        self._grid_layout.removeWidget(old_card)
        old_card.deleteLater()

        # Build new card and insert at same position
        new_card = self._make_card(char)
        self._grid_layout.addWidget(new_card, grid_row, grid_col)
        self._card_widgets[card_id] = new_card

    def _make_card(self, char: dict) -> QFrame:
        is_selected = char is self.selected_character

        card = QFrame()
        card.setObjectName("combatantCard")
        card.setProperty("selected", "true" if is_selected else "false")
        card.setFixedWidth(220)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        # --- Name ---
        name_lbl = QLabel(char["name"])
        name_lbl.setObjectName("cardName")
        layout.addWidget(name_lbl)

        # --- HP bar ---
        hp = char["hp"]
        max_hp = char["max_hp"]
        temp_hp = char.get("temp_hp", 0)

        hp_row = QHBoxLayout()
        hp_row.setSpacing(4)

        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(max(max_hp, 1))
        bar.setValue(max(hp, 0))
        bar.setFormat(f"{hp} / {max_hp}")
        bar.setTextVisible(True)

        # Determine color class
        if hp <= 0:
            chunk_name = "hp_dead"
        elif hp / max_hp <= 0.25:
            chunk_name = "hp_red"
        elif hp / max_hp <= 0.50:
            chunk_name = "hp_orange"
        else:
            chunk_name = "hp_green"

        bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: "
            + {
                "hp_green": "#2ecc71",
                "hp_orange": "#e67e22",
                "hp_red": "#e74c3c",
                "hp_dead": "#555",
            }[chunk_name]
            + "; border-radius: 3px; }"
        )
        hp_row.addWidget(bar, stretch=1)

        if temp_hp and temp_hp > 0:
            temp_lbl = QLabel(f"(+{temp_hp} temp)")
            temp_lbl.setObjectName("secondary")
            temp_lbl.setStyleSheet("color: #5bc8f5; font-size: 10px;")
            hp_row.addWidget(temp_lbl)

        layout.addLayout(hp_row)

        # --- AC ---
        ac_lbl = QLabel(f"AC: {char['ac']}")
        ac_lbl.setObjectName("secondary")
        layout.addWidget(ac_lbl)

        # --- Conditions ---
        conditions = char.get("conditions", [])
        if conditions:
            cond_row = QHBoxLayout()
            cond_row.setSpacing(3)
            cond_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
            for cond in conditions:
                badge = QLabel(cond)
                badge.setObjectName("conditionBadge")
                cond_row.addWidget(badge)
            cond_row.addStretch()
            layout.addLayout(cond_row)

        # --- Spell slots ---
        slots = {k: v for k, v in (char.get("spell_slots") or {}).items() if v > 0}
        if slots:
            slots_text = "  ".join(f"LV{lv}({cnt})" for lv, cnt in sorted(slots.items()))
            slots_lbl = QLabel(slots_text)
            slots_lbl.setObjectName("secondary")
            slots_lbl.setStyleSheet("color: #a0c4ff; font-size: 11px;")
            layout.addWidget(slots_lbl)

        # --- Ability Scores ---
        ability_scores = char.get("Ability Scores") or {}
        if ability_scores:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #0f3460;")
            layout.addWidget(sep)
            scores_list = list(ability_scores.items())
            for row_idx in range(2):
                chunk = scores_list[row_idx * 3: row_idx * 3 + 3]
                if chunk:
                    row_text = "  ".join(f"{a[:3]} {m:+d}" for a, m in chunk)
                    row_lbl = QLabel(row_text)
                    row_lbl.setObjectName("secondary")
                    row_lbl.setStyleSheet("font-family: monospace; font-size: 11px; color: #a0a0b0;")
                    layout.addWidget(row_lbl)

        # --- Saving Throws ---
        saving_throws = char.get("Saving Throws") or {}
        if saving_throws:
            st_header = QLabel("Saves:")
            st_header.setStyleSheet("color: #c9a84c; font-size: 10px; font-weight: bold;")
            layout.addWidget(st_header)
            throws_list = list(saving_throws.items())
            for row_idx in range(2):
                chunk = throws_list[row_idx * 3: row_idx * 3 + 3]
                if chunk:
                    row_text = "  ".join(f"{a[:3]} {m:+d}" for a, m in chunk)
                    row_lbl = QLabel(row_text)
                    row_lbl.setStyleSheet("font-family: monospace; font-size: 11px; color: #a0a0b0;")
                    layout.addWidget(row_lbl)

        # --- Click to select (install event filter on all children) ---
        card.mousePressEvent = lambda event, c=char: self._select_character(c)
        # Propagate clicks from child labels to card
        for child in card.findChildren(QWidget):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        return card

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def run(self):
        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyleSheet(QSS)

        self._build_window()
        self._rebuild_cards()

        self._window.show()
        sys.exit(app.exec())
