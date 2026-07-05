import json
import random
import sys
from datetime import datetime
from pathlib import Path

import CharacterSheetCreator
import Definitions
from Combat.ConditionRules import ConditionRule
from Combat.Definitions import Action, BasicCombatantData, Condition, ExtendedCombatantData
from Combat.Rules import Rule, group_by_category, load_rules
from Features.Equipment import Armor

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
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
QFrame#combatantCard[dead="true"] {
    background-color: #0e0e18;
    border: 2px solid #2a2a2a;
}
QFrame#combatantCard[dying="true"] {
    background-color: #1a0e2e;
    border: 2px solid #7a2fa0;
}
QFrame#combatantCard[stabilized="true"] {
    background-color: #0e1a18;
    border: 2px solid #2a6a5a;
}
QFrame#combatantCard[selected="true"] {
    background-color: #1e2d5a;
    border: 2px solid #e94560;
}
QFrame#combatantCard[active="true"] {
    background-color: #2a2010;
    border: 2px solid #c9a84c;
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
    color: #1a1a2e;
    font-size: 10px;
    font-weight: bold;
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
QPushButton:disabled {
    background-color: #0a1a30;
    color: #555;
    border-color: #0a2540;
}

/* Primary buttons (damage) */
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

/* Heal button */
QPushButton#healBtn {
    background-color: #1a3d2e;
    border: 1px solid #4caf82;
    color: #4caf82;
    font-weight: bold;
}
QPushButton#healBtn:hover {
    background-color: #204d38;
}
QPushButton#healBtn:pressed {
    background-color: #102a1e;
}

/* Temp HP button */
QPushButton#tempHpBtn {
    background-color: #1a2e3d;
    border: 1px solid #4a9fc4;
    color: #4a9fc4;
    font-weight: bold;
}
QPushButton#tempHpBtn:hover {
    background-color: #20384d;
}
QPushButton#tempHpBtn:pressed {
    background-color: #10202e;
}

/* Death save — fail */
QPushButton#deathFailBtn {
    background-color: #3d1a1a;
    border: 1px solid #c04040;
    color: #c04040;
    font-weight: bold;
}
QPushButton#deathFailBtn:hover { background-color: #4d2020; }
QPushButton#deathFailBtn:pressed { background-color: #2a1010; }
QPushButton#deathFailBtn:disabled { color: #555; border-color: #333; background: #1a1a1a; }

/* Death save — success */
QPushButton#deathSuccessBtn {
    background-color: #1a3d1a;
    border: 1px solid #40c040;
    color: #40c040;
    font-weight: bold;
}
QPushButton#deathSuccessBtn:hover { background-color: #204d20; }
QPushButton#deathSuccessBtn:pressed { background-color: #102a10; }
QPushButton#deathSuccessBtn:disabled { color: #555; border-color: #333; background: #1a1a1a; }

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
        resume_log_path: str | None = None,
    ):
        self.combatants_per_column = combatants_per_column
        self._resume_log_path = resume_log_path

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

        # --- Phase / initiative state ---
        self.phase: str = "INITIATIVE"
        self.initiative_order: list[dict] = []
        self.current_turn_idx: int = 0

        log_dir = Path("CombatLogs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = log_dir / f"combat_log_{timestamp}.json"
        self._write_log({})

        # card widget registry: maps id(char_dict) -> QFrame
        self._card_widgets: dict[int, QFrame] = {}

        # initiative input registry: maps id(char_dict) -> QLineEdit
        self._initiative_inputs: dict[int, QLineEdit] = {}

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def _add_from_character_sheet(self, character_sheet):
        from Spells.SpellFactory import SpellFactory
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

        # Apply weapon masteries to live weapon objects
        weapons = list(character_sheet.weapons)
        if character_sheet.weapon_masteries:
            mastery_types = {type(m) for m in character_sheet.weapon_masteries}
            for w in weapons:
                if type(w) in mastery_types:
                    w.player_has_mastery = True

        # Pre-compute spell levels (display_name, level, Ability enum)
        spells_with_level = []
        spell_objects: dict[str, object] = {}
        for spell_name, ability, ruling in character_sheet.spells:
            display_name = getattr(spell_name, "value", str(spell_name))
            try:
                spell_obj = SpellFactory.create(spell_name, ability, ruling)
                spells_with_level.append((display_name, spell_obj.level, ability))
                spell_objects[display_name] = spell_obj
            except Exception:
                spells_with_level.append((display_name, 0, ability))

        self.characters.append(
            {
                "name": character_sheet.character_name,
                "hp": hp,
                "max_hp": hp,
                "ac": ac,
                "temp_hp": 0,
                "conditions": [],
                "death_saves_fail": 0,
                "death_saves_success": 0,
                "spell_slots": spell_slots,
                "Ability Scores": {
                    ability.short_name: character.get_ability_score(ability)
                    for ability in Definitions.Ability
                },
                "Saving Throws": {
                    ability.short_name: character.get_saving_throw_modifier(ability)
                    for ability in Definitions.Ability
                },
                "_is_player": True,
                "_stat_block": character,
                "_weapons_objects": weapons,
                "class_levels": {
                    cls.value: lvl
                    for cls, lvl in character_sheet.level_per_class.items()
                },
                "subclass": character_sheet.character_subclass or "",
                "proficiency_bonus": character.get_proficiency_bonus(),
                "speed": character_sheet.speed or "",
                "size": character_sheet.size.value if character_sheet.size else "",
                "spells_with_level": spells_with_level,
                "_spell_objects": spell_objects,
                "features": [
                    getattr(f, "name", type(f).__name__)
                    for f in character_sheet.features
                ],
                "_feature_objects": list(character_sheet.features),
                "invocations": list(character_sheet.invocations),
            }
        )

    def _add_basic_combatant(self, combatant: BasicCombatantData):
        char = {
            "name": combatant.name,
            "hp": combatant.hp,
            "max_hp": combatant.max_hp,
            "ac": combatant.ac,
            "temp_hp": combatant.temp_hp,
            "conditions": [cond.value for cond in combatant.conditions],
            "death_saves_fail": 0,
            "death_saves_success": 0,
            "spell_slots": combatant.spell_slots,
            "Ability Scores": combatant.ability_scores,
            "Saving Throws": combatant.saving_throws,
        }
        if isinstance(combatant, ExtendedCombatantData):
            char.update({
                "cr": combatant.cr,
                "monster_type": combatant.monster_type,
                "ac_note": combatant.ac_note,
                "hp_formula": combatant.hp_formula,
                "speed": combatant.speed,
                "skills": combatant.skills,
                "damage_vulnerabilities": combatant.damage_vulnerabilities,
                "damage_resistances": combatant.damage_resistances,
                "damage_immunities": combatant.damage_immunities,
                "condition_immunities": combatant.condition_immunities,
                "senses": combatant.senses,
                "languages": combatant.languages,
                "traits": combatant.traits,
                "actions": combatant.actions,
                "bonus_actions": combatant.bonus_actions,
                "reactions": combatant.reactions,
                "legendary_actions": combatant.legendary_actions,
                "legendary_resistances": combatant.legendary_resistances,
                "lair_actions": combatant.lair_actions,
                "mythic_actions": combatant.mythic_actions,
            })
        self.characters.append(char)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def _write_log(self, data: dict):
        data["round_number"] = self.round_number
        data["combatants"] = [{k: v for k, v in c.items() if not k.startswith("_")} for c in self.characters]
        self.log_file.write_text(json.dumps(data, indent=2))

    def _current_turn_name(self) -> str | None:
        if self.phase != "COMBAT" or not self.initiative_order:
            return None
        return self.initiative_order[self.current_turn_idx]["name"]

    def _log_event(self, text: str, note_turn: bool = True):
        data = json.loads(self.log_file.read_text())
        key = f"round_{self.round_number}"
        turn_name = self._current_turn_name() if note_turn else None
        entry = f"[{turn_name}'s turn] {text}" if turn_name else text
        data.setdefault(key, []).append(entry)
        self._write_log(data)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _select_character(self, char: dict):
        self.selected_character = char
        self.selected_label.setText(f"Selected: {char['name']}")
        self._more_info_btn.setEnabled(True)
        self._refresh_cards()

    def _show_more_info(self):
        if not self.selected_character:
            return
        char = self.selected_character

        dlg = QDialog(self._window)
        dlg.setWindowTitle(char["name"])
        dlg.setMinimumWidth(520)
        dlg.resize(560, 660)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(0, 0, 0, 8)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(3)

        def add_header(text: str):
            lbl = QLabel(text.upper())
            lbl.setObjectName("sectionHeader")
            lay.addWidget(lbl)

        def add_field(label: str, value: str):
            lbl = QLabel(f"<b>{label}:</b> {value}")
            lbl.setWordWrap(True)
            lay.addWidget(lbl)

        def add_ability(name: str, description: str):
            lbl = QLabel(f"<b><i>{name}.</i></b> {description}")
            lbl.setWordWrap(True)
            lbl.setContentsMargins(0, 2, 0, 2)
            lay.addWidget(lbl)

        def add_divider():
            lay.addWidget(self._make_divider())

        def make_expandable(header_text: str, content_widget: QWidget) -> QWidget:
            wrapper = QWidget()
            wl = QVBoxLayout(wrapper)
            wl.setContentsMargins(0, 0, 0, 0)
            wl.setSpacing(0)
            btn = QPushButton(f"▶  {header_text}")
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setStyleSheet(
                "QPushButton { text-align: left; padding: 2px 4px; background: transparent; "
                "border: none; color: #eaeaea; font-size: 12px; }"
                "QPushButton:hover { color: #c9a84c; }"
                "QPushButton:checked { color: #c9a84c; }"
            )
            content_widget.setVisible(False)

            def toggle(checked: bool, _btn=btn, _hw=header_text, _cw=content_widget):
                _btn.setText(f"{'▼' if checked else '▶'}  {_hw}")
                _cw.setVisible(checked)

            btn.toggled.connect(toggle)
            wl.addWidget(btn)
            wl.addWidget(content_widget)
            return wrapper

        # --- Basic stats ---
        hp_str = f"{char['hp']} / {char['max_hp']}"
        if char.get("temp_hp"):
            hp_str += f"  (+{char['temp_hp']} temp)"
        add_field("HP", hp_str)

        ac_val = str(char["ac"])
        if char.get("ac_note"):
            ac_val = f"{ac_val} ({char['ac_note']})"
        add_field("AC", ac_val)

        if char.get("conditions"):
            add_field("Conditions", ", ".join(char["conditions"]))

        if char.get("spell_slots"):
            active = {k: v for k, v in char["spell_slots"].items() if v > 0}
            if active:
                add_field("Spell Slots", "  ".join(f"L{k}×{v}" for k, v in active.items()))

        scores = char.get("Ability Scores", {})
        saves = char.get("Saving Throws", {})
        if scores:
            add_divider()
            add_header("Ability Scores")
            td  = "border:1px solid #0f3460;text-align:center;padding:2px 7px;"
            tds = "border:1px solid #0f3460;text-align:center;padding:2px 7px;color:#a0a0b0;font-size:11px;"
            tdt = "border:1px solid #0f3460;border-top:2px solid #0f3460;text-align:center;padding:2px 7px;color:#a0a0b0;font-size:11px;"
            cells_h = cells_v = cells_m = cells_s = ""
            for key, val in scores.items():
                mod = (val - 10) // 2
                sv  = saves.get(key, mod)
                cells_h += f"<td style='{td}'><b>{key}</b></td>"
                cells_v += f"<td style='{td}'>{val}</td>"
                cells_m += f"<td style='{tds}'>{mod:+}</td>"
                cells_s += f"<td style='{tdt}'>{sv:+}</td>"
            html = (
                f"<table style='border-collapse:collapse'>"
                f"<tr>{cells_h}</tr>"
                f"<tr>{cells_v}</tr>"
                f"<tr>{cells_m}</tr>"
            )
            if saves:
                html += f"<tr>{cells_s}</tr>"
            html += "</table>"
            lbl = QLabel(html)
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lay.addWidget(lbl)
            if saves:
                legend = QLabel(
                    "<span style='color:#555;font-size:10px'>"
                    "score / mod / save</span>"
                )
                legend.setTextFormat(Qt.TextFormat.RichText)
                lay.addWidget(legend)

        # --- Player stats (only present for character-sheet combatants) ---
        if "_is_player" in char:
            sb = char.get("_stat_block")

            add_divider()
            if char.get("class_levels"):
                add_field("Class", ", ".join(
                    f"{cls} {lvl}" for cls, lvl in char["class_levels"].items()
                ))
            if char.get("subclass"):
                add_field("Subclass", char["subclass"])
            if char.get("proficiency_bonus"):
                add_field("Proficiency Bonus", f"+{char['proficiency_bonus']}")
            if char.get("speed"):
                add_field("Speed", f"{char['speed']} ft.")
            if char.get("size"):
                add_field("Size", char["size"])

            # All skills table
            if sb:
                add_divider()
                add_header("Skills")
                td  = "border:1px solid #0f3460;padding:2px 7px;"
                tdr = f"{td}text-align:right;"
                tdc = f"{td}text-align:center;font-size:10px;"
                header_row = (
                    f"<tr>"
                    f"<th style='{td}color:#c9a84c'>Skill</th>"
                    f"<th style='{tdr}color:#c9a84c'>Mod</th>"
                    f"<th style='{tdc}color:#c9a84c'></th>"
                    f"</tr>"
                )
                skill_rows = ""
                for skill in Definitions.Skill:
                    mod    = sb.get_skill_modifier(skill)
                    has_exp = sb.has_expertise_in_skill(skill)
                    is_prof = sb.is_proficient_in_skill(skill)
                    if has_exp:
                        name_html = f"<b>{skill.value}</b>"
                        prof_html = f"<span style='color:#d4a747;font-weight:bold'>Exp</span>"
                    elif is_prof:
                        name_html = f"<b>{skill.value}</b>"
                        prof_html = f"<span style='color:#7ecb7e'>Prof</span>"
                    else:
                        name_html = skill.value
                        prof_html = f"<span style='color:#555'>—</span>"
                    skill_rows += (
                        f"<tr>"
                        f"<td style='{td}'>{name_html}</td>"
                        f"<td style='{tdr}'>{mod:+}</td>"
                        f"<td style='{tdc}'>{prof_html}</td>"
                        f"</tr>"
                    )
                skills_lbl = QLabel(
                    f"<table style='border-collapse:collapse'>{header_row}{skill_rows}</table>"
                )
                skills_lbl.setTextFormat(Qt.TextFormat.RichText)
                lay.addWidget(skills_lbl)

            # Spell DC and spell attack bonus
            spells_with_level = char.get("spells_with_level", [])
            if spells_with_level and sb:
                seen: dict = {}
                for _, _, ability in spells_with_level:
                    if ability not in seen:
                        seen[ability] = (
                            sb.calculate_difficulty_class_for_ability(ability),
                            sb.calculate_attack_bonus_for_ability(ability),
                        )
                if seen:
                    add_divider()
                    add_field("Spell DC", "  ".join(
                        f"DC {dc} ({ab.short_name})" for ab, (dc, _) in seen.items()
                    ))
                    add_field("Spell Attack", "  ".join(
                        f"{atk:+} ({ab.short_name})" for ab, (_, atk) in seen.items()
                    ))

            # Spells as expandable items grouped by level
            spell_objects_map = char.get("_spell_objects", {})
            if spells_with_level:
                add_divider()
                add_header("Spells")
                current_level = -1
                for spell_name, level, _ in sorted(spells_with_level, key=lambda s: (s[1], s[0])):
                    if level != current_level:
                        current_level = level
                        lvl_label = "Cantrips" if level == 0 else f"Level {level}"
                        lbl = QLabel(f"<b style='color:#c9a84c'>{lvl_label}</b>")
                        lbl.setTextFormat(Qt.TextFormat.RichText)
                        lay.addWidget(lbl)
                    spell_obj = spell_objects_map.get(spell_name)
                    if spell_obj is not None:
                        sw = QWidget()
                        swl = QVBoxLayout(sw)
                        swl.setContentsMargins(16, 2, 0, 4)
                        swl.setSpacing(2)
                        school_color = spell_obj.get_school_color(spell_obj.school)
                        meta_lbl = QLabel(
                            f"<span style='color:{school_color}'>{spell_obj.school}</span>"
                            f"  <span style='color:#a0a0b0'>Cast:</span> {spell_obj.casting_time}"
                            f"  <span style='color:#a0a0b0'>Range:</span> {spell_obj.range}"
                            f"  <span style='color:#a0a0b0'>Duration:</span> {spell_obj.duration}"
                            f"  <span style='color:#a0a0b0'>Components:</span> {spell_obj.components}"
                        )
                        meta_lbl.setTextFormat(Qt.TextFormat.RichText)
                        meta_lbl.setWordWrap(True)
                        swl.addWidget(meta_lbl)
                        if spell_obj.description:
                            desc_lbl = QLabel(spell_obj.description)
                            desc_lbl.setWordWrap(True)
                            desc_lbl.setStyleSheet("color: #c0c0c0; font-size: 11px;")
                            swl.addWidget(desc_lbl)
                        lay.addWidget(make_expandable(spell_name, sw))
                    else:
                        lay.addWidget(QLabel(f"  • {spell_name}"))

            # Weapons as expandable items
            weapons_objs = char.get("_weapons_objects", [])
            if weapons_objs and sb:
                add_divider()
                add_header("Weapons")
                for weapon in weapons_objs:
                    stats = weapon.stats()
                    to_hit = weapon.calculate_total_attack_roll_bonus_int(sb)
                    ab_mod, ab_name = weapon._calculate_ability_modifier_bonus(sb)
                    dmg = f"{stats.damage_roll.value} {ab_mod:+} ({ab_name})"
                    header_text = f"{stats.name}  1d20{to_hit:+}  dmg {dmg}"

                    ww = QWidget()
                    wwl = QVBoxLayout(ww)
                    wwl.setContentsMargins(16, 2, 0, 4)
                    wwl.setSpacing(2)

                    prof_str = "Proficient" if weapon.player_is_proficient else "Not proficient"
                    type_line = "  ·  ".join(
                        [stats.weapon_type.value, stats.damage_type.value, prof_str]
                    )
                    type_lbl = QLabel(f"<span style='color:#a0a0b0'>{type_line}</span>")
                    type_lbl.setTextFormat(Qt.TextFormat.RichText)
                    type_lbl.setWordWrap(True)
                    wwl.addWidget(type_lbl)

                    if stats.additional_description:
                        desc_lbl = QLabel(stats.additional_description)
                        desc_lbl.setWordWrap(True)
                        desc_lbl.setStyleSheet("color: #c0c0c0; font-size: 11px;")
                        wwl.addWidget(desc_lbl)

                    if stats.mastery:
                        mark = "✓" if getattr(weapon, "player_has_mastery", False) else "✗"
                        mastery_lbl = QLabel(
                            f"<span style='color:#a0a0b0'>Mastery:</span> "
                            f"<span style='color:#c9a84c'>{stats.mastery.value} {mark}</span> "
                            f"<span style='color:#c0c0c0'>— {stats.mastery.description}</span>"
                        )
                        mastery_lbl.setTextFormat(Qt.TextFormat.RichText)
                        mastery_lbl.setWordWrap(True)
                        mastery_lbl.setStyleSheet("font-size: 11px;")
                        wwl.addWidget(mastery_lbl)

                    if stats.properties:
                        prop_header_lbl = QLabel("Properties:")
                        prop_header_lbl.setStyleSheet("color: #a0a0b0; font-size: 11px;")
                        wwl.addWidget(prop_header_lbl)
                        for prop in stats.properties:
                            prop_lbl = QLabel(
                                f"<span style='color:#c9a84c'>{prop.value}</span> "
                                f"<span style='color:#c0c0c0'>— {prop.description}</span>"
                            )
                            prop_lbl.setTextFormat(Qt.TextFormat.RichText)
                            prop_lbl.setStyleSheet("font-size: 11px;")
                            prop_lbl.setWordWrap(True)
                            prop_lbl.setContentsMargins(10, 0, 0, 0)
                            wwl.addWidget(prop_lbl)

                    lay.addWidget(make_expandable(header_text, ww))

            # Features as expandable items
            feat_objs = char.get("_feature_objects", [])
            if feat_objs:
                add_divider()
                add_header("Features")
                for feat in feat_objs:
                    feat_name = getattr(feat, "name", type(feat).__name__)
                    get_desc = getattr(feat, "get_description", None)
                    if get_desc is not None and sb:
                        try:
                            desc_text = get_desc(sb)
                            fw = QWidget()
                            fwl = QVBoxLayout(fw)
                            fwl.setContentsMargins(16, 2, 0, 4)
                            fwl.setSpacing(2)
                            origin = getattr(feat, "origin", "")
                            if origin:
                                orig_lbl = QLabel(f"<i style='color:#a0a0b0'>{origin}</i>")
                                orig_lbl.setTextFormat(Qt.TextFormat.RichText)
                                fwl.addWidget(orig_lbl)
                            desc_lbl = QLabel(desc_text)
                            desc_lbl.setWordWrap(True)
                            desc_lbl.setStyleSheet("color: #c0c0c0; font-size: 11px;")
                            fwl.addWidget(desc_lbl)
                            lay.addWidget(make_expandable(feat_name, fw))
                        except Exception:
                            lay.addWidget(QLabel(f"• {feat_name}"))
                    else:
                        lay.addWidget(QLabel(f"• {feat_name}"))
            elif char.get("features"):
                add_divider()
                add_header("Features")
                for name in char["features"]:
                    lay.addWidget(QLabel(f"• {name}"))

            if char.get("invocations"):
                add_divider()
                add_header("Invocations")
                for inv in char["invocations"]:
                    lbl = QLabel(f"• {inv}")
                    lay.addWidget(lbl)

        # --- Extended stats (only present for ExtendedCombatantData) ---
        if "cr" in char:
            add_divider()
            for key, label in [
                ("monster_type", "Type"),
                ("cr", "CR"),
                ("speed", "Speed"),
                ("hp_formula", "Hit Dice"),
                ("senses", "Senses"),
                ("languages", "Languages"),
            ]:
                if char.get(key):
                    add_field(label, char[key])

            if char.get("skills"):
                add_header("Skills")
                td  = "border:1px solid #0f3460;padding:2px 8px;"
                tdr = f"{td}text-align:right;"
                rows = "".join(
                    f"<tr><td style='{td}'>{k}</td><td style='{tdr}'>{v:+}</td></tr>"
                    for k, v in char["skills"].items()
                )
                skills_lbl = QLabel(
                    f"<table style='border-collapse:collapse'>{rows}</table>"
                )
                skills_lbl.setTextFormat(Qt.TextFormat.RichText)
                lay.addWidget(skills_lbl)

            for key, label in [
                ("damage_vulnerabilities", "Vulnerabilities"),
                ("damage_resistances", "Resistances"),
                ("damage_immunities", "Damage Immunities"),
                ("condition_immunities", "Condition Immunities"),
            ]:
                val = char.get(key, [])
                if val:
                    add_field(label, ", ".join(val))

            if char.get("legendary_resistances"):
                add_field("Legendary Resistances", str(char["legendary_resistances"]))

            for section_key, section_label in [
                ("traits", "Traits"),
                ("actions", "Actions"),
                ("bonus_actions", "Bonus Actions"),
                ("reactions", "Reactions"),
                ("legendary_actions", "Legendary Actions"),
                ("lair_actions", "Lair Actions"),
                ("mythic_actions", "Mythic Actions"),
            ]:
                abilities = char.get(section_key, [])
                if abilities:
                    add_divider()
                    add_header(section_label)
                    for ab in abilities:
                        add_ability(ab.get("name", ""), ab.get("description", ""))

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(30)
        close_btn.clicked.connect(dlg.accept)
        outer.addWidget(close_btn)

        dlg.exec()

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

        if "Concentrating" in self.selected_character.get("conditions", []):
            self._concentration_check_dialog(self.selected_character, dmg)

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
        header_lbl.setStyleSheet(
            "color: #c9a84c; font-weight: bold; font-size: 13px;"
        )
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
                self._log_event(
                    f"{name} loses concentration (DC {dc}, rolled {roll})"
                )
                self._refresh_selected_card()
            dialog.accept()

        def _cancel():
            dialog.reject()

        confirm_btn.clicked.connect(_confirm)
        cancel_btn.clicked.connect(_cancel)

        dialog.exec()

    def _apply_heal(self):
        if not self.selected_character:
            return
        try:
            heal = int(self.heal_input.text())
        except ValueError:
            return

        char = self.selected_character
        was_downed = self._char_death_state(char) != "alive"

        char["hp"] = min(char["hp"] + heal, char["max_hp"])
        self.history.append((Action.HEAL, heal))

        if was_downed and char["hp"] > 0:
            char["death_saves_fail"] = 0
            char["death_saves_success"] = 0
            self._log_event(f"{char['name']} is resurrected with {char['hp']} HP")
        else:
            self._log_event(f"{char['name']} heals {heal} HP")

        self._refresh_selected_card()

    def _apply_failed_death_save(self, char: dict):
        if self._char_death_state(char) != "dying":
            return
        self._select_character(char)
        char["death_saves_fail"] = min(char.get("death_saves_fail", 0) + 1, 3)
        self.history.append((Action.DEATH_SAVE_FAIL, None))
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
        elif action == Action.DEATH_SAVE_FAIL:
            char["death_saves_fail"] = max(char.get("death_saves_fail", 0) - 1, 0)
        elif action == Action.DEATH_SAVE_SUCCESS:
            char["death_saves_success"] = max(char.get("death_saves_success", 0) - 1, 0)

        last_event = data[key].pop()
        self._write_log(data)
        print(f"Undid action: {last_event}")
        self._refresh_selected_card()

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
        self._refresh_turn()

    def _show_current_log(self):
        """Display the round-by-round event history of the active log file."""
        if not self.log_file.exists():
            QMessageBox.information(self._window, "Combat Log", "No log data yet.")
            return
        data = json.loads(self.log_file.read_text())
        round_keys = sorted(
            (k for k in data if k.startswith("round_") and k.split("_", 1)[1].isdigit()),
            key=lambda k: int(k.split("_", 1)[1]),
        )

        dlg = QDialog(self._window)
        dlg.setWindowTitle(f"Combat Log — {self.log_file.name}")
        dlg.setMinimumSize(480, 500)
        dlg.setStyleSheet(QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        text = QTextEdit()
        text.setReadOnly(True)
        if not round_keys:
            text.setPlainText("No events logged yet.")
        else:
            lines = []
            for key in round_keys:
                round_num = key.split("_", 1)[1]
                lines.append(f"Round {round_num}")
                for event in data[key]:
                    lines.append(f"  • {event}")
                lines.append("")
            text.setPlainText("\n".join(lines).rstrip())
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.exec()

    def _show_rules(self):
        """Browse the rules glossary, grouped by category and searchable by name/text."""
        if not hasattr(self, "_rules_cache"):
            self._rules_cache: list[Rule] = load_rules()
        rules = self._rules_cache

        dlg = QDialog(self._window)
        dlg.setWindowTitle("Rules")
        dlg.setMinimumSize(760, 560)
        dlg.setStyleSheet(QSS)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(8)

        search_box = QLineEdit()
        search_box.setPlaceholderText("Search rules…")
        outer.addWidget(search_box)

        body = QHBoxLayout()
        body.setSpacing(10)
        outer.addLayout(body)

        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setMinimumWidth(260)
        body.addWidget(tree, stretch=1)

        detail = QTextEdit()
        detail.setReadOnly(True)
        body.addWidget(detail, stretch=2)

        category_items: dict[str, QTreeWidgetItem] = {}
        for category, category_rules in group_by_category(rules).items():
            cat_item = QTreeWidgetItem([category])
            cat_item.setFirstColumnSpanned(True)
            tree.addTopLevelItem(cat_item)
            category_items[category] = cat_item
            for rule in category_rules:
                rule_item = QTreeWidgetItem([rule.name])
                rule_item.setData(0, Qt.ItemDataRole.UserRole, rule)
                cat_item.addChild(rule_item)
        tree.expandAll()

        def show_rule(rule: Rule):
            detail.setHtml(
                f"<b style='color:#c9a84c; font-size:14px;'>{rule.name}</b> "
                f"<span style='color:#a0a0b0;'>[{rule.category}]</span>"
                f"<br><br>{rule.body.replace(chr(10) + chr(10), '<br><br>')}"
            )

        def on_selection_changed():
            items = tree.selectedItems()
            if not items:
                return
            rule = items[0].data(0, Qt.ItemDataRole.UserRole)
            if rule is not None:
                show_rule(rule)

        tree.itemSelectionChanged.connect(on_selection_changed)

        def apply_filter(query: str):
            query = query.strip().lower()
            for category, cat_item in category_items.items():
                any_visible = False
                for i in range(cat_item.childCount()):
                    child = cat_item.child(i)
                    rule = child.data(0, Qt.ItemDataRole.UserRole)
                    visible = rule.matches(query)
                    child.setHidden(not visible)
                    any_visible = any_visible or visible
                cat_item.setHidden(not any_visible)
                if query:
                    cat_item.setExpanded(any_visible)

        search_box.textChanged.connect(apply_filter)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        outer.addWidget(close_btn)

        dlg.exec()

    def _load_log_from_path(self, path: str):
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
        # When loading a log we jump straight into COMBAT with the loaded order
        self.phase = "COMBAT"
        self.initiative_order = list(self.characters)
        self.current_turn_idx = 0
        self._switch_to_combat()

    # ------------------------------------------------------------------
    # Initiative phase
    # ------------------------------------------------------------------
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
        header.setStyleSheet(
            "color: #c9a84c; font-size: 16px; font-weight: bold;"
        )
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
            name_lbl.setStyleSheet(
                "color: #c9a84c; font-weight: bold;"
            )
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
            while j < len(order_with_initiative) and order_with_initiative[j][0] == order_with_initiative[i][0]:
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

        info = QLabel("Some combatants tied on initiative.\nDrag rows to set the turn order within each tied group.")
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

        # --- Left: scrollable area (initiative or card grid) ---
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Build the card grid container (hidden until combat starts)
        self._cards_container = QWidget()
        self._grid_layout = QGridLayout(self._cards_container)
        self._grid_layout.setSpacing(8)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._cards_container.hide()

        # Build and show the initiative widget
        self._initiative_widget = self._build_initiative_widget()
        self._scroll_area.setWidget(self._initiative_widget)

        root_layout.addWidget(self._scroll_area, stretch=1)

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

        self._more_info_btn = QPushButton("More Info")
        self._more_info_btn.setEnabled(False)
        self._more_info_btn.clicked.connect(self._show_more_info)
        panel_layout.addWidget(self._more_info_btn)

        # Round indicator
        self.round_label = QLabel(f"Round {self.round_number}")
        self.round_label.setStyleSheet("color: #c9a84c; font-weight: bold; font-size: 12px;")
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

        self._init_tracker_layout = QVBoxLayout()
        self._init_tracker_layout.setContentsMargins(0, 0, 0, 0)
        self._init_tracker_layout.setSpacing(1)
        tracker_outer.addLayout(self._init_tracker_layout)

        panel_layout.addWidget(self._init_tracker_container)

        panel_layout.addWidget(self._make_divider())

        # Damage section
        panel_layout.addWidget(self._section_header("Damage"))
        self.damage_input = QLineEdit()
        self.damage_input.setPlaceholderText("Amount...")
        panel_layout.addWidget(self.damage_input)
        self.damage_input.returnPressed.connect(self._apply_damage)
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
        self.heal_input.returnPressed.connect(self._apply_heal)
        heal_btn = QPushButton("Apply Heal")
        heal_btn.setObjectName("healBtn")
        heal_btn.clicked.connect(self._apply_heal)
        panel_layout.addWidget(heal_btn)

        panel_layout.addWidget(self._make_divider())

        # Temp HP section
        panel_layout.addWidget(self._section_header("Temp HP"))
        self.temp_hp_input = QLineEdit()
        self.temp_hp_input.setPlaceholderText("Amount...")
        panel_layout.addWidget(self.temp_hp_input)
        self.temp_hp_input.returnPressed.connect(self._apply_temp_hp)
        temp_hp_btn = QPushButton("Add Temp HP")
        temp_hp_btn.setObjectName("tempHpBtn")
        temp_hp_btn.clicked.connect(self._apply_temp_hp)
        panel_layout.addWidget(temp_hp_btn)

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

        rules_btn = QPushButton("Rules")
        rules_btn.clicked.connect(self._show_rules)
        panel_layout.addWidget(rules_btn)

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

        self._refresh_initiative_tracker()

    def _refresh_cards(self):
        """Update border/background of all cards to reflect selection, active-turn, and dead state."""
        for char in self.characters:
            card = self._card_widgets.get(id(char))
            if card is None:
                continue
            death_state = self._char_death_state(char)
            is_selected = char is self.selected_character
            is_active = (
                self.phase == "COMBAT"
                and self.initiative_order
                and self.initiative_order[self.current_turn_idx] is char
            )
            card.setProperty("dead",       "true" if death_state == "dead"       else "false")
            card.setProperty("dying",      "true" if death_state == "dying"      else "false")
            card.setProperty("stabilized", "true" if death_state == "stabilized" else "false")
            card.setProperty("selected", "true" if is_selected and not is_active else "false")
            card.setProperty("active", "true" if is_active else "false")
            card.style().unpolish(card)
            card.style().polish(card)

    def _rebuild_card(self, char: dict):
        """Rebuild a specific combatant card in-place (after stat changes)."""
        card_id = id(char)
        old_card = self._card_widgets.get(card_id)
        if old_card is None:
            return
        idx = self._grid_layout.indexOf(old_card)
        if idx < 0:
            return
        pos = self._grid_layout.getItemPosition(idx)
        grid_row, grid_col = pos[0], pos[1]
        self._grid_layout.removeWidget(old_card)
        old_card.deleteLater()
        new_card = self._make_card(char)
        self._grid_layout.addWidget(new_card, grid_row, grid_col)
        self._card_widgets[card_id] = new_card

    def _refresh_selected_card(self):
        """Rebuild only the selected card in-place."""
        if self.selected_character is not None:
            self._rebuild_card(self.selected_character)

    def _refresh_initiative_tracker(self):
        """Rebuild the initiative order tracker widget rows."""
        # Clear existing rows
        while self._init_tracker_layout.count():
            item = self._init_tracker_layout.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

        if not self.initiative_order:
            return

        total = len(self.initiative_order)
        current_idx = self.current_turn_idx
        self._turn_counter_label.setText(f"Turn {current_idx + 1} / {total}")

        for idx, char in enumerate(self.initiative_order):
            is_active = idx == current_idx
            death_state = self._char_death_state(char)
            already_gone = idx < current_idx

            if is_active:
                dot_color = "#c9a84c"
                name_color = "#c9a84c"
            elif death_state == "dead":
                dot_color = "#555"
                name_color = "#555"
            elif already_gone:
                dot_color = "#a0c4ff"
                name_color = "#a0c4ff"
            else:
                dot_color = "#eaeaea"
                name_color = "#eaeaea"

            row_w = QWidget()
            row_layout = QHBoxLayout(row_w)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {dot_color}; font-size: 8px;")
            dot.setFixedWidth(12)
            row_layout.addWidget(dot)

            display_name = char["name"][:20] + ("…" if len(char["name"]) > 20 else "")
            name_lbl = QLabel(display_name)
            name_lbl.setStyleSheet(f"color: {name_color}; font-size: 10px;")
            row_layout.addWidget(name_lbl, stretch=1)

            self._init_tracker_layout.addWidget(row_w)

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

    # Condition badge color map
    _CONDITION_COLORS: dict[str, str] = {
        "Poisoned":      "#1a5c1a",
        "Frightened":    "#7a3d00",
        "Charmed":       "#5c1a7a",
        "Blinded":       "#3a3a3a",
        "Concentrating": "#1a3a7a",
        "Paralyzed":     "#7a1a1a",
        "Stunned":       "#7a1a1a",
        "Grappled":      "#5c4a00",
        "Prone":         "#5c4a00",
    }

    def _show_condition_info(self, condition_name: str):
        rule = ConditionRule.from_name(condition_name)
        if rule is None:
            return
        heading, body = rule.heading, rule.description

        dlg = QDialog(self._window)
        dlg.setWindowTitle(condition_name)
        dlg.setMinimumWidth(380)
        dlg.setStyleSheet(QSS)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        title_lbl = QLabel(heading)
        title_lbl.setStyleSheet("font-weight: bold; color: #c9a84c; font-size: 13px;")
        layout.addWidget(title_lbl)

        divider = QFrame()
        divider.setObjectName("divider")
        layout.addWidget(divider)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet("color: #c0c0c0; font-size: 12px;")
        layout.addWidget(body_lbl)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(28)
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.exec()

    @staticmethod
    def _char_death_state(char: dict) -> str:
        """Return 'alive', 'dying', 'stabilized', or 'dead'."""
        if char["hp"] > 0:
            return "alive"
        if char.get("death_saves_fail", 0) >= 3:
            return "dead"
        if char.get("death_saves_success", 0) >= 3:
            return "stabilized"
        return "dying"

    def _make_card(self, char: dict) -> QFrame:
        hp = char["hp"]
        death_state = self._char_death_state(char)
        is_dead       = death_state == "dead"
        is_dying      = death_state == "dying"
        is_stabilized = death_state == "stabilized"
        is_selected = char is self.selected_character
        is_active = (
            self.phase == "COMBAT"
            and self.initiative_order
            and self.initiative_order[self.current_turn_idx] is char
        )

        card = QFrame()
        card.setObjectName("combatantCard")
        card.setProperty("dead",       "true" if is_dead       else "false")
        card.setProperty("dying",      "true" if is_dying      else "false")
        card.setProperty("stabilized", "true" if is_stabilized else "false")
        card.setProperty("selected", "true" if is_selected and not is_active else "false")
        card.setProperty("active", "true" if is_active else "false")
        card.setFixedWidth(220)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        # --- Name ---
        if is_dead:
            display_name = "☠ " + char["name"]
            name_style = "color: #555; font-weight: bold; font-size: 13px;"
        elif is_dying:
            display_name = "💀 " + char["name"]
            name_style = "color: #b070e0; font-weight: bold; font-size: 13px;"
        elif is_stabilized:
            display_name = "😴 " + char["name"]
            name_style = "color: #4a9080; font-weight: bold; font-size: 13px;"
        else:
            display_name = char["name"]
            name_style = ""
        name_lbl = QLabel(display_name)
        name_lbl.setObjectName("cardName")
        if name_style:
            name_lbl.setStyleSheet(name_style)
        layout.addWidget(name_lbl)

        # --- Death save pips + buttons (dying / stabilized) ---
        if is_dying or is_stabilized:
            fail    = char.get("death_saves_fail", 0)
            success = char.get("death_saves_success", 0)
            pips_lbl = QLabel(
                f"<span style='color:#c04040'>{'●' * fail}{'○' * (3 - fail)}</span>"
                f"  "
                f"<span style='color:#40c040'>{'●' * success}{'○' * (3 - success)}</span>"
            )
            pips_lbl.setTextFormat(Qt.TextFormat.RichText)
            pips_lbl.setStyleSheet("font-size: 11px; letter-spacing: 2px;")
            layout.addWidget(pips_lbl)

        if is_dying:
            btn_row = QHBoxLayout()
            btn_row.setSpacing(4)
            fail_btn = QPushButton("✗ Fail")
            fail_btn.setObjectName("deathFailBtn")
            fail_btn.setFixedHeight(24)
            fail_btn.clicked.connect(lambda _=False, c=char: self._apply_failed_death_save(c))
            save_btn = QPushButton("✓ Save")
            save_btn.setObjectName("deathSuccessBtn")
            save_btn.setFixedHeight(24)
            save_btn.clicked.connect(lambda _=False, c=char: self._apply_success_death_save(c))
            btn_row.addWidget(fail_btn)
            btn_row.addWidget(save_btn)
            layout.addLayout(btn_row)

        # --- HP bar ---
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

        if hp <= 0:
            chunk_color = "#555"
        elif hp / max_hp <= 0.25:
            chunk_color = "#e74c3c"
        elif hp / max_hp <= 0.50:
            chunk_color = "#e67e22"
        else:
            chunk_color = "#2ecc71"

        bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {chunk_color}; border-radius: 3px; }}"
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
                badge_color = self._CONDITION_COLORS.get(cond, "#7a5c00")
                has_rule = ConditionRule.from_name(cond) is not None
                if has_rule:
                    badge = QPushButton(cond)
                    badge.setFlat(True)
                    badge.setStyleSheet(
                        f"QPushButton {{ background-color: {badge_color}; color: #ffffff;"
                        " border-radius: 3px; padding: 1px 4px; font-size: 10px;"
                        " border: none; cursor: pointer; }}"
                        f"QPushButton:hover {{ background-color: {badge_color}cc; }}"
                    )
                    badge.setCursor(Qt.CursorShape.PointingHandCursor)
                    badge.clicked.connect(
                        lambda _=False, c=cond: self._show_condition_info(c)
                    )
                else:
                    badge = QLabel(cond)
                    badge.setStyleSheet(
                        f"background-color: {badge_color}; color: #ffffff;"
                        " border-radius: 3px; padding: 1px 4px; font-size: 10px;"
                    )
                cond_row.addWidget(badge)
            cond_row.addStretch()
            layout.addLayout(cond_row)

        # --- Spell slots ---
        slots = {k: v for k, v in (char.get("spell_slots") or {}).items() if v > 0}
        if slots:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #0f3460;")
            layout.addWidget(sep)
            slots_header = QLabel("Slots:")
            slots_header.setStyleSheet("color: #c9a84c; font-size: 10px; font-weight: bold;")
            layout.addWidget(slots_header)
            slots_text = "  ".join(f"LV{lv}({cnt})" for lv, cnt in sorted(slots.items()))
            slots_lbl = QLabel(slots_text)
            slots_lbl.setStyleSheet("color: #a0c4ff; font-size: 11px;")
            layout.addWidget(slots_lbl)

        # --- Ability Scores / Saving Throws combined as mod/save ---
        ability_scores = char.get("Ability Scores") or {}
        saving_throws = char.get("Saving Throws") or {}
        if ability_scores:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #0f3460;")
            layout.addWidget(sep)

            # Detect raw scores (any value > 10 means raw, not modifier)
            raw_values = list(ability_scores.values())
            is_raw = any(v > 10 for v in raw_values)

            def to_mod(v: int) -> int:
                return (v - 10) // 2

            entries = []
            for name, val in ability_scores.items():
                mod = to_mod(val) if is_raw else val
                abbr = name[:3].upper()
                # Saving throws are already modifiers — do not convert
                if saving_throws:
                    save = saving_throws.get(name, mod)
                    entries.append((abbr, mod, save, True))
                else:
                    entries.append((abbr, mod, mod, False))

            for row_idx in range(2):
                chunk = entries[row_idx * 3: row_idx * 3 + 3]
                if chunk:
                    if chunk[0][3]:  # has saving throws
                        row_text = "  ".join(f"{abbr} {m:+d}/{s:+d}" for abbr, m, s, _ in chunk)
                    else:
                        row_text = "  ".join(f"{abbr} {m:+d}" for abbr, m, *_ in chunk)
                    row_lbl = QLabel(row_text)
                    row_lbl.setStyleSheet("font-family: monospace; font-size: 10px; color: #a0a0b0;")
                    layout.addWidget(row_lbl)

        # --- Click to select ---
        card.mousePressEvent = lambda event, c=char: self._select_character(c)
        for child in card.findChildren(QWidget):
            if not isinstance(child, QPushButton):
                child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        return card

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def run(self):
        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyleSheet(QSS)

        self._build_window()

        if self._resume_log_path:
            self._load_log_from_path(self._resume_log_path)

        self._window.show()
        sys.exit(app.exec())
