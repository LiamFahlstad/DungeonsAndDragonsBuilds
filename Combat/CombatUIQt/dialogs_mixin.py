"""Dialogs mixin for CombatAppQt."""

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

import Core.Definitions as Definitions
from Combat.Definitions import ConditionRule
from Core.Definitions import DamageType
from Model.Creatures.MonsterAbilities import DcMonsterAbility, extract_dc_from_text
from Combat.Rules import Rule, group_by_category, load_rules
from Combat.PlayerCombatant import weapon_summary
from Core.Definitions import DiceRollCondition, Die
from Utils.DamageCalculator import probability_of_success

from .stats import (
    SPELL_SLOT_LEVELS,
    damage_dealt_key,
    damage_taken_key,
    spell_slots_used_key,
)
from .settings import SETTING_SECTIONS
from .styles import QSS
from Core.Rules import ability_modifier
from .state import CombatWindowState
from .tree_filter import filter_category_tree


def _display(value) -> str:
    """Render an enum member (Skill/DamageType/Condition/...) or a plain
    value the same way — falls back to str() for plain strings/ints and for
    values that came back from a resumed JSON log (already plain strings)."""
    return value.value if hasattr(value, "value") else str(value)


def _ability_entry(ab) -> tuple[str, str]:
    """A trait/action/... entry is a MonsterAbility fresh from a monster class,
    or a plain {"name":..., "description":...} dict once it's round-tripped
    through a saved combat log (JSON has no dataclass concept)."""
    if isinstance(ab, dict):
        return ab.get("name", ""), ab.get("description", "")
    return ab.name, ab.description


def _creature_type_text(char: dict) -> str:
    """'Beast' + note 'Swarm of Tiny' -> 'Swarm of Tiny Beasts'; 'Dragon' + note
    'Metallic' -> 'Dragon (Metallic)'; no monster_type -> the note verbatim (a
    multi-type entry like 'Celestial or Fey or Fiend (Your Choice)')."""
    monster_type = char.get("monster_type")
    note = char.get("monster_type_note") or ""
    if not monster_type:
        return note
    creature_text = _display(monster_type)
    swarm_prefix = ""
    extra_notes = []
    for segment in note.split("; "):
        segment = segment.strip()
        if not segment:
            continue
        if segment.lower().startswith("swarm of"):
            swarm_prefix = segment
        else:
            extra_notes.append(segment)
    if swarm_prefix:
        creature_text = f"{swarm_prefix} {creature_text}s"
    if extra_notes:
        creature_text = f"{creature_text} ({', '.join(extra_notes)})"
    return creature_text


def _monster_type_text(char: dict) -> str:
    parts = []
    if char.get("size"):
        parts.append(_display(char["size"]))
    creature_text = _creature_type_text(char)
    if creature_text:
        parts.append(creature_text)
    text = " ".join(parts)
    if char.get("alignment"):
        alignment_text = _display(char["alignment"])
        text = f"{text}, {alignment_text}" if text else alignment_text
    return text


def _speed_text(char: dict) -> str:
    parts = []
    if char.get("speed_ground_ft") is not None:
        parts.append(f"{char['speed_ground_ft']} ft.")
    elif char.get("speed") not in (None, ""):
        # Player characters store ground speed as a plain "speed" int, not
        # the speed_ground_ft/climb/fly breakdown monsters use.
        parts.append(f"{char['speed']} ft.")
    if char.get("speed_climb_ft") is not None:
        parts.append(f"climb {char['speed_climb_ft']} ft.")
    if char.get("speed_fly_ft") is not None:
        parts.append(f"fly {char['speed_fly_ft']} ft.")
    text = ", ".join(parts)
    special = char.get("speed_special_rules")
    if special:
        text = f"{text} ({special})" if text else special
    return text


def _damage_entry_text(entry) -> str:
    """A damage_resistances/immunities/vulnerabilities entry is a DamageTypeEntry
    fresh from a monster class, or a plain dict once resumed from a saved log."""
    if isinstance(entry, dict):
        types, note = entry.get("damage_types", []), entry.get("note", "")
    else:
        types, note = entry.damage_types, entry.note
    text = ", ".join(_display(t) for t in types)
    if note:
        text = f"{text} {note}" if text else note
    return text


def _ability_field(ab, key: str):
    """Read a field off a MonsterAbility subclass instance, or off the plain
    dict it becomes once round-tripped through a saved combat log."""
    if isinstance(ab, dict):
        return ab.get(key)
    return getattr(ab, key, None)


_HIT_TABLE_ACS = range(10, 21)
_SAVE_TABLE_MODIFIERS = range(-5, 11)


def _probability_row_html(header_cells: list[str], value_cells: list[str]) -> str:
    td = "border:1px solid #0f3460;text-align:center;padding:2px 6px;"
    header_html = "".join(
        f"<th style='{td}color:#c9a84c'>{h}</th>" for h in header_cells
    )
    value_html = "".join(f"<td style='{td}'>{v}</td>" for v in value_cells)
    return f"<table style='border-collapse:collapse'><tr>{header_html}</tr><tr>{value_html}</tr></table>"


def _hit_chance_table_html(attack_bonus: int) -> str:
    """Chance the monster's attack roll (1d20 + attack_bonus) hits, for a
    spread of target ACs — powered by Utils.DamageCalculator."""
    values = [
        probability_of_success(
            difficulty_class=ac,
            die=Die.D20,
            condition=DiceRollCondition.NEUTRAL,
            bonus=attack_bonus,
        )
        for ac in _HIT_TABLE_ACS
    ]
    return _probability_row_html(
        [f"AC {ac}" for ac in _HIT_TABLE_ACS],
        [f"{p * 100:.0f}%" for p in values],
    )


def _save_chance_table_html(dc: int) -> str:
    """Chance a target's saving throw (1d20 + modifier) FAILS against the
    monster's DC, for a spread of target save modifiers -- i.e. the
    monster's chance of landing the effect, not the target's chance of
    resisting it. Powered by Utils.DamageCalculator."""
    values = [
        1
        - probability_of_success(
            difficulty_class=dc,
            die=Die.D20,
            condition=DiceRollCondition.NEUTRAL,
            bonus=modifier,
        )
        for modifier in _SAVE_TABLE_MODIFIERS
    ]
    return _probability_row_html(
        [f"{modifier:+}" for modifier in _SAVE_TABLE_MODIFIERS],
        [f"{p * 100:.0f}%" for p in values],
    )


def _ability_dc(ab) -> int | None:
    """DC for a save-based ability: the `dc` field on a SavingThrowEffect, or
    (for a DcMonsterAbility, live or resumed from a saved log as a plain
    dict) the DC pulled out of its free-text description. A prose `dc` (a
    summon's "equals your spell save DC") falls through to the description,
    which names no number, so it has none."""
    dc = _ability_field(ab, "dc")
    if isinstance(dc, int):
        return dc
    if isinstance(ab, DcMonsterAbility):
        return ab.extract_dc()
    if isinstance(ab, dict):
        return extract_dc_from_text(ab.get("description", ""))
    return None


def _ability_probability_table_html(ab) -> str | None:
    """A MeleeAttack/RangedAttack gets a hit-chance-by-AC table; a
    SavingThrowEffect or DcMonsterAbility gets a table of the target's
    save-failure chance (i.e. the monster's chance of landing the effect)
    by save modifier; anything else (traits, Multiattack, plain abilities,
    ...) gets none."""
    attack_bonus = _ability_field(ab, "attack_bonus")
    if attack_bonus is not None:
        return _hit_chance_table_html(attack_bonus)
    dc = _ability_dc(ab)
    if dc is not None:
        return _save_chance_table_html(dc)
    return None


class _InfoPanel:
    """The More Info dialog's scrolling column: labelled fields, section
    headers, dividers, stat-block abilities and expandable sections."""

    def __init__(self, content: QWidget, make_divider: Callable[[], QFrame]):
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(3)
        self._make_divider = make_divider

    def add(self, widget: QWidget):
        self.layout.addWidget(widget)

    def header(self, text: str):
        lbl = QLabel(text.upper())
        lbl.setObjectName("sectionHeader")
        self.add(lbl)

    def section(self, text: str):
        """A divider, then a section header."""
        self.divider()
        self.header(text)

    def field(self, label: str, value: str):
        lbl = QLabel(f"<b>{label}:</b> {value}")
        lbl.setWordWrap(True)
        self.add(lbl)

    def ability(self, name: str, description: str):
        lbl = QLabel(f"<b><i>{name}.</i></b> {description}")
        lbl.setWordWrap(True)
        lbl.setContentsMargins(0, 2, 0, 2)
        self.add(lbl)

    def bullet(self, text: str):
        self.add(QLabel(f"• {text}"))

    def divider(self):
        self.add(self._make_divider())

    def expandable(self, header_text: str, content_widget: QWidget):
        """`content_widget` under a ▶/▼ toggle button, collapsed at first."""
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

        def toggle(checked: bool):
            btn.setText(f"{'▼' if checked else '▶'}  {header_text}")
            content_widget.setVisible(checked)

        btn.toggled.connect(toggle)
        wl.addWidget(btn)
        wl.addWidget(content_widget)
        self.add(wrapper)


def _detail_box(spacing: int = 2) -> tuple[QWidget, QVBoxLayout]:
    """The indented body of an expandable section."""
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(16, 2, 0, 4)
    layout.setSpacing(spacing)
    return box, layout


def _rich_label(html: str, word_wrap: bool = False, style: str = "") -> QLabel:
    lbl = QLabel(html)
    lbl.setTextFormat(Qt.TextFormat.RichText)
    if word_wrap:
        lbl.setWordWrap(True)
    if style:
        lbl.setStyleSheet(style)
    return lbl


def _description_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet("color: #c0c0c0; font-size: 11px;")
    return lbl


def _add_vitals(panel: _InfoPanel, char: dict):
    """HP, AC, conditions and remaining spell slots."""
    hp_str = f"{char['hp']} / {char['max_hp']}"
    if char.get("temp_hp"):
        hp_str += f"  (+{char['temp_hp']} temp)"
    panel.field("HP", hp_str)

    ac_val = str(char["ac"])
    if char.get("ac_note"):
        ac_val = f"{ac_val} ({char['ac_note']})"
    panel.field("AC", ac_val)

    if char.get("conditions"):
        panel.field("Conditions", ", ".join(char["conditions"]))

    if char.get("spell_slots"):
        active = {k: v for k, v in char["spell_slots"].items() if v > 0}
        if active:
            panel.field(
                "Spell Slots", "  ".join(f"L{k}×{v}" for k, v in active.items())
            )


def _add_ability_score_table(panel: _InfoPanel, char: dict):
    """Score / modifier / save per ability (saves only when the stat block
    has them)."""
    scores = char.get("Ability Scores", {})
    saves = char.get("Saving Throws", {})
    if not scores:
        return
    panel.section("Ability Scores")
    td = "border:1px solid #0f3460;text-align:center;padding:2px 7px;"
    tds = "border:1px solid #0f3460;text-align:center;padding:2px 7px;color:#a0a0b0;font-size:11px;"
    tdt = "border:1px solid #0f3460;border-top:2px solid #0f3460;text-align:center;padding:2px 7px;color:#a0a0b0;font-size:11px;"
    cells_h = cells_v = cells_m = cells_s = ""
    for key, val in scores.items():
        mod = ability_modifier(val)
        sv = saves.get(key, mod)
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
    panel.add(_rich_label(html))
    if saves:
        panel.add(
            _rich_label(
                "<span style='color:#555;font-size:10px'>score / mod / save</span>"
            )
        )


# ---------------------------------------------------------------------------
# Player characters (character-sheet combatants)


def _add_player_details(panel: _InfoPanel, char: dict):
    sb = char.get("_stat_block")
    _add_player_summary(panel, char)
    if sb:
        _add_player_skill_table(panel, sb)
        _add_spellcasting_numbers(panel, char, sb)
    _add_player_spells(panel, char)
    if sb:
        _add_player_weapons(panel, char, sb)
    _add_player_features(panel, char, sb)
    if char.get("invocations"):
        panel.section("Invocations")
        for inv in char["invocations"]:
            panel.bullet(_display(inv))


def _add_player_summary(panel: _InfoPanel, char: dict):
    panel.divider()
    if char.get("class_levels"):
        panel.field(
            "Class",
            ", ".join(f"{cls} {lvl}" for cls, lvl in char["class_levels"].items()),
        )
    if char.get("subclass"):
        panel.field("Subclass", char["subclass"])
    if char.get("proficiency_bonus"):
        panel.field("Proficiency Bonus", f"+{char['proficiency_bonus']}")
    if char.get("speed"):
        panel.field("Speed", f"{char['speed']} ft.")
    if char.get("size"):
        panel.field("Size", char["size"])


def _add_player_skill_table(panel: _InfoPanel, sb):
    """Every skill's modifier, marking proficiency and expertise."""
    panel.section("Skills")
    td = "border:1px solid #0f3460;padding:2px 7px;"
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
        mod = sb.get_skill_modifier(skill)
        if sb.has_expertise_in_skill(skill):
            name_html = f"<b>{skill.value}</b>"
            prof_html = "<span style='color:#d4a747;font-weight:bold'>Exp</span>"
        elif sb.is_proficient_in_skill(skill):
            name_html = f"<b>{skill.value}</b>"
            prof_html = "<span style='color:#7ecb7e'>Prof</span>"
        else:
            name_html = skill.value
            prof_html = "<span style='color:#555'>—</span>"
        skill_rows += (
            f"<tr>"
            f"<td style='{td}'>{name_html}</td>"
            f"<td style='{tdr}'>{mod:+}</td>"
            f"<td style='{tdc}'>{prof_html}</td>"
            f"</tr>"
        )
    panel.add(
        _rich_label(
            f"<table style='border-collapse:collapse'>{header_row}{skill_rows}</table>"
        )
    )


def _add_spellcasting_numbers(panel: _InfoPanel, char: dict, sb):
    """Spell save DC and spell attack bonus for each spellcasting ability."""
    by_ability: dict = {}
    for _, _, ability in char.get("spells_with_level", []):
        if ability not in by_ability:
            by_ability[ability] = (
                sb.calculate_difficulty_class_for_ability(ability),
                sb.calculate_attack_bonus_for_ability(ability),
            )
    if not by_ability:
        return
    panel.divider()
    panel.field(
        "Spell DC",
        "  ".join(f"DC {dc} ({ab.short_name})" for ab, (dc, _) in by_ability.items()),
    )
    panel.field(
        "Spell Attack",
        "  ".join(f"{atk:+} ({ab.short_name})" for ab, (_, atk) in by_ability.items()),
    )


def _add_player_spells(panel: _InfoPanel, char: dict):
    """Spells grouped by level, each expandable to its details."""
    spells_with_level = char.get("spells_with_level", [])
    if not spells_with_level:
        return
    spell_objects = char.get("_spell_objects", {})
    panel.section("Spells")
    current_level = -1
    for spell_name, level, _ in sorted(spells_with_level, key=lambda s: (s[1], s[0])):
        if level != current_level:
            current_level = level
            level_label = "Cantrips" if level == 0 else f"Level {level}"
            panel.add(_rich_label(f"<b style='color:#c9a84c'>{level_label}</b>"))
        spell_obj = spell_objects.get(spell_name)
        if spell_obj is None:
            panel.add(QLabel(f"  • {spell_name}"))
        else:
            panel.expandable(spell_name, _spell_details(spell_obj))


def _spell_details(spell_obj) -> QWidget:
    box, layout = _detail_box()
    school_color = spell_obj.get_school_color(spell_obj.school)
    layout.addWidget(
        _rich_label(
            f"<span style='color:{school_color}'>{spell_obj.school}</span>"
            f"  <span style='color:#a0a0b0'>Cast:</span> {spell_obj.casting_time}"
            f"  <span style='color:#a0a0b0'>Range:</span> {spell_obj.range}"
            f"  <span style='color:#a0a0b0'>Duration:</span> {spell_obj.duration}"
            f"  <span style='color:#a0a0b0'>Components:</span> {spell_obj.components}",
            word_wrap=True,
        )
    )
    if spell_obj.description:
        layout.addWidget(_description_label(spell_obj.description))
    if spell_obj.additional_ruling:
        layout.addWidget(
            _rich_label(
                f"<span style='color:#c9a84c'>Ruling:</span> "
                f"<span style='color:#c0c0c0'>{spell_obj.additional_ruling}</span>",
                word_wrap=True,
                style="font-size: 11px;",
            )
        )
    return box


def _add_player_weapons(panel: _InfoPanel, char: dict, sb):
    weapons = char.get("_weapons_objects", [])
    if not weapons:
        return
    panel.section("Weapons")
    for weapon in weapons:
        panel.expandable(weapon_summary(weapon, sb), _weapon_details(weapon, char, sb))


def _weapon_details(weapon, char: dict, sb) -> QWidget:
    box, layout = _detail_box()
    prof_str = "Proficient" if weapon.is_proficient(sb) else "Not proficient"
    type_line = "  ·  ".join(
        [weapon.weapon_type.value, weapon.damage_type.value, prof_str]
    )
    layout.addWidget(
        _rich_label(f"<span style='color:#a0a0b0'>{type_line}</span>", word_wrap=True)
    )
    if weapon.description_text:
        layout.addWidget(_description_label(weapon.description_text))
    if weapon.mastery:
        mark = "✓" if weapon.has_mastery(char.get("_weapon_masteries", [])) else "✗"
        layout.addWidget(
            _rich_label(
                f"<span style='color:#a0a0b0'>Mastery:</span> "
                f"<span style='color:#c9a84c'>{weapon.mastery.value} {mark}</span> "
                f"<span style='color:#c0c0c0'>— {weapon.mastery.description}</span>",
                word_wrap=True,
                style="font-size: 11px;",
            )
        )
    if weapon.properties:
        prop_header_lbl = QLabel("Properties:")
        prop_header_lbl.setStyleSheet("color: #a0a0b0; font-size: 11px;")
        layout.addWidget(prop_header_lbl)
        for prop in weapon.properties:
            prop_lbl = _rich_label(
                f"<span style='color:#c9a84c'>{prop.value}</span> "
                f"<span style='color:#c0c0c0'>— {prop.description}</span>",
                style="font-size: 11px;",
            )
            prop_lbl.setWordWrap(True)
            prop_lbl.setContentsMargins(10, 0, 0, 0)
            layout.addWidget(prop_lbl)
    return box


def _add_player_features(panel: _InfoPanel, char: dict, sb):
    """Each feature expandable to its description; listed by name alone
    without a stat block, or when its description is None or fails."""
    feature_objects = char.get("_feature_objects", [])
    if not feature_objects:
        if char.get("features"):
            panel.section("Features")
            for name in char["features"]:
                panel.bullet(name)
        return
    panel.section("Features")
    for feature in feature_objects:
        description = None
        if sb:
            try:
                description = feature.get_description(sb)
            except Exception:
                pass
        if description is None:
            panel.bullet(feature.name)
            continue
        box, layout = _detail_box()
        if feature.origin:
            layout.addWidget(
                _rich_label(f"<i style='color:#a0a0b0'>{feature.origin}</i>")
            )
        layout.addWidget(_description_label(description))
        panel.expandable(feature.name, box)


# ---------------------------------------------------------------------------
# Monsters (ExtendedCombatantData)

_MONSTER_ABILITY_SECTIONS = (
    ("traits", "Traits"),
    ("actions", "Actions"),
    ("bonus_actions", "Bonus Actions"),
    ("reactions", "Reactions"),
    ("legendary_actions", "Legendary Actions"),
    ("lair_actions", "Lair Actions"),
    ("mythic_actions", "Mythic Actions"),
)


def _add_monster_details(panel: _InfoPanel, char: dict):
    _add_monster_summary(panel, char)
    if char.get("skills"):
        _add_monster_skill_table(panel, char["skills"])
    _add_monster_defenses(panel, char)
    if char.get("legendary_resistances"):
        panel.field("Legendary Resistances", str(char["legendary_resistances"]))
    for key, label in _MONSTER_ABILITY_SECTIONS:
        abilities = char.get(key, [])
        if abilities:
            panel.section(label)
            for ab in abilities:
                _add_monster_ability(panel, ab)


def _add_monster_summary(panel: _InfoPanel, char: dict):
    panel.divider()
    type_text = _monster_type_text(char)
    if type_text:
        panel.field("Type", type_text)
    if char.get("cr"):
        panel.field("CR", char["cr"])
    speed_text = _speed_text(char)
    if speed_text:
        panel.field("Speed", speed_text)
    for key, label in (
        ("hp_formula", "Hit Dice"),
        ("senses", "Senses"),
        ("languages", "Languages"),
    ):
        if char.get(key):
            panel.field(label, char[key])
    if char.get("description"):
        desc_lbl = QLabel(char["description"])
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-style: italic; color: #c0c0c0;")
        panel.add(desc_lbl)


def _add_monster_skill_table(panel: _InfoPanel, skills: dict):
    panel.header("Skills")
    td = "border:1px solid #0f3460;padding:2px 8px;"
    tdr = f"{td}text-align:right;"
    rows = "".join(
        f"<tr><td style='{td}'>{_display(k)}</td><td style='{tdr}'>{v:+}</td></tr>"
        for k, v in skills.items()
    )
    panel.add(_rich_label(f"<table style='border-collapse:collapse'>{rows}</table>"))


def _add_monster_defenses(panel: _InfoPanel, char: dict):
    for key, label in (
        ("damage_vulnerabilities", "Vulnerabilities"),
        ("damage_resistances", "Resistances"),
        ("damage_immunities", "Damage Immunities"),
    ):
        entries = char.get(key, [])
        if entries:
            panel.field(label, "; ".join(_damage_entry_text(e) for e in entries))
    if char.get("condition_immunities"):
        panel.field(
            "Condition Immunities",
            ", ".join(_display(c) for c in char["condition_immunities"]),
        )


def _add_monster_ability(panel: _InfoPanel, ab):
    """A trait/action/...: plain text, or for an attack or a save with a DC,
    expandable to its hit or save-failure chances."""
    name, desc = _ability_entry(ab)
    table_html = _ability_probability_table_html(ab)
    if table_html is None:
        panel.ability(name, desc)
        return

    attack_bonus = _ability_field(ab, "attack_bonus")
    if attack_bonus is not None:
        header_suffix = f"{attack_bonus:+} to hit"
        caption_text = "Chance to hit, by target AC"
    else:
        header_suffix = f"DC {_ability_dc(ab)}"
        caption_text = "Target's chance to fail the save, by save modifier"

    box, layout = _detail_box(spacing=4)
    desc_lbl = QLabel(desc)
    desc_lbl.setWordWrap(True)
    layout.addWidget(desc_lbl)
    caption_lbl = QLabel(caption_text)
    caption_lbl.setStyleSheet("color: #a0a0b0; font-size: 10px;")
    layout.addWidget(caption_lbl)
    layout.addWidget(_rich_label(table_html))
    panel.expandable(f"{name}  ({header_suffix})", box)


class DialogsMixin(CombatWindowState):
    """Mixin for dialog windows."""

    def _show_add_combatant_dialog(self):
        """Quickly add a free-text combatant — a name plus optional HP/AC —
        for ad hoc sources/targets that don't need a full sheet or monster
        (e.g. 'a door', an NPC improvised mid-session)."""
        if self.phase == "PARTY":
            return  # only in an encounter
        dlg = QDialog(self._window)
        dlg.setWindowTitle("Add Combatant")
        dlg.setStyleSheet(QSS)
        dlg.setFixedWidth(300)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Name:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g. Wooden Door, Bandit Captain...")
        layout.addWidget(name_input)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(6)
        stats_row.addWidget(QLabel("HP:"))
        hp_input = QLineEdit("10")
        hp_input.setFixedWidth(60)
        stats_row.addWidget(hp_input)
        stats_row.addWidget(QLabel("AC:"))
        ac_input = QLineEdit("10")
        ac_input.setFixedWidth(60)
        stats_row.addWidget(ac_input)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.setObjectName("primaryBtn")
        cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(add_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        def do_add():
            name = name_input.text().strip()
            if not name:
                return
            try:
                hp = int(hp_input.text())
            except ValueError:
                hp = 10
            try:
                ac = int(ac_input.text())
            except ValueError:
                ac = 10
            self._add_ad_hoc_combatant(name, hp=hp, ac=ac)
            dlg.accept()

        add_btn.clicked.connect(do_add)
        name_input.returnPressed.connect(do_add)
        cancel_btn.clicked.connect(dlg.reject)

        name_input.setFocus()
        dlg.exec()

    def _show_settings_dialog(self):
        """Settings that change how the window behaves. Each one takes effect
        (and is saved) the moment it's changed."""
        dlg = QDialog(self._window)
        dlg.setWindowTitle("Settings")
        dlg.setStyleSheet(QSS)
        dlg.setFixedWidth(360)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        def set_setting(name: str, checked: bool):
            setattr(self.settings, name, checked)
            if self._settings_store is not None:
                self.settings.save(self._settings_store)
            if name == "source_follows_turn":
                self._follow_turn_with_source()
            self._apply_panel_settings()

        for index, (section, infos) in enumerate(SETTING_SECTIONS):
            if index:
                layout.addWidget(self._make_divider())
            header = QLabel(section)
            header.setObjectName("sectionHeader")
            layout.addWidget(header)
            for info in infos:
                box = QCheckBox(info.label)
                box.setObjectName(info.name)
                box.setChecked(getattr(self.settings, info.name))
                box.toggled.connect(
                    lambda checked, name=info.name: set_setting(name, checked)
                )
                layout.addWidget(box)
                hint = QLabel(info.hint)
                hint.setWordWrap(True)
                hint.setStyleSheet("color: #a0a0b0; font-size: 11px;")
                layout.addWidget(hint)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.exec()

    def _show_more_info(self):
        if not self.selected_character:
            self._show_status("Nothing to show: left-click a card to pick a source.")
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
        panel = _InfoPanel(content, self._make_divider)

        _add_vitals(panel, char)
        _add_ability_score_table(panel, char)
        if "_is_player" in char:
            _add_player_details(panel, char)
        if "cr" in char:
            _add_monster_details(panel, char)

        panel.layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(30)
        close_btn.clicked.connect(dlg.accept)
        outer.addWidget(close_btn)

        dlg.exec()

    def _show_statistics(self):
        """Display battle statistics for every combatant, split into an 'Encounter'
        group (this fight only) and a 'Players' group (lifetime aggregates), each
        broken into one tab per stat category so wide tables don't get cramped."""
        dlg = QDialog(self._window)
        dlg.setWindowTitle("Statistics")
        dlg.setMinimumSize(1150, 520)
        dlg.setStyleSheet(QSS)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(10)

        tabs = QTabWidget()

        # Damage/Spells columns are bounded (fixed DamageType/level sets), so they can
        # be built once and reused for both the Encounter and Players tabs. Column
        # "key" is either a flat stats key (str) or a nested-dict lookup (key, name).
        damage_columns = (
            [("Damage Dealt", "damage_dealt")]
            + [
                (f"Dealt: {dtype.value}", damage_dealt_key(dtype.value))
                for dtype in DamageType
            ]
            + [("Damage Taken", "damage_taken")]
            + [
                (f"Taken: {dtype.value}", damage_taken_key(dtype.value))
                for dtype in DamageType
            ]
        )
        healing_columns = [
            ("Healing Done", "healing_done"),
            ("Healing Received", "healing_received"),
            ("Temp HP Granted", "temp_hp_granted"),
            ("Temp HP Received", "temp_hp_received"),
        ]
        outcome_columns = [
            ("Knockouts", "knockouts"),
            ("Times Downed", "times_downed"),
            ("Deaths", "deaths"),
        ]

        def _stats_for(characters, stats_dict_or_none, char):
            if stats_dict_or_none is not None:
                return stats_dict_or_none.get(char.get("name", ""), {})
            return char.get("stats") or {}

        def _condition_columns(characters, stats_dict_or_none):
            """Conditions are open-ended (spells can apply custom pseudo-conditions by
            name), so their columns are computed per-tab from whichever condition
            names actually show up for these characters, instead of a fixed list."""
            names = set()
            for char in characters:
                stats = _stats_for(characters, stats_dict_or_none, char)
                names.update(stats.get("conditions_given_by_name", {}).keys())
                names.update(stats.get("conditions_received_by_name", {}).keys())
            sorted_names = sorted(names)
            return (
                [
                    ("Given (Total)", "conditions_given"),
                    ("Received (Total)", "conditions_received"),
                ]
                + [
                    (f"Given: {name}", ("conditions_given_by_name", name))
                    for name in sorted_names
                ]
                + [
                    (f"Received: {name}", ("conditions_received_by_name", name))
                    for name in sorted_names
                ]
            )

        def _spell_columns(characters, stats_dict_or_none):
            """Spell slot levels are a fixed 1-9 range, but which spells were actually
            cast is open-ended, so the per-spell columns are computed per-tab like
            Conditions above."""
            names = set()
            for char in characters:
                stats = _stats_for(characters, stats_dict_or_none, char)
                names.update(stats.get("spells_cast_by_name", {}).keys())
            sorted_names = sorted(names)
            return (
                [("Spell Slots Used", "spell_slots_used")]
                + [
                    (f"Level {level}", spell_slots_used_key(level))
                    for level in SPELL_SLOT_LEVELS
                ]
                + [("Spells Cast", "spells_cast")]
                + [
                    (f"Cast: {name}", ("spells_cast_by_name", name))
                    for name in sorted_names
                ]
            )

        # (label, columns_fn) — columns_fn(characters, stats_dict_or_none) -> [(header, key), ...]
        categories = [
            ("Damage", lambda *_: damage_columns),
            ("Healing", lambda *_: healing_columns),
            ("Conditions", _condition_columns),
            ("Spells", _spell_columns),
            ("Outcomes", lambda *_: outcome_columns),
        ]

        def _column_value(stats, key):
            """key is either a flat stats key, or a (dict_key, name) nested lookup."""
            if isinstance(key, tuple):
                dict_key, name = key
                return stats.get(dict_key, {}).get(name, 0)
            return stats.get(key, 0)

        # Helper function to build a stat table widget for a single category
        def _build_table_widget(
            characters, stats_dict_or_none, columns, is_players_tab=False
        ):
            """Build a scrollable table for the given characters and (header, key)
            columns. If is_players_tab and no player log, return a label instead."""
            if is_players_tab and not self.player_log_file:
                lbl = QLabel(
                    "No player log active — run with --player-log to track the party across sessions."
                )
                lbl.setWordWrap(True)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                return lbl

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            content = QWidget()
            grid = QGridLayout(content)
            grid.setHorizontalSpacing(14)
            grid.setVerticalSpacing(6)

            headers = ["Name"] + [header for header, _ in columns]
            for col, text in enumerate(headers):
                lbl = QLabel(text)
                lbl.setStyleSheet("color: #c9a84c; font-weight: bold;")
                grid.addWidget(lbl, 0, col)

            for row, char in enumerate(characters, start=1):
                stats = _stats_for(characters, stats_dict_or_none, char)
                values = [char.get("name", "")] + [
                    _column_value(stats, key) for _, key in columns
                ]
                for col, value in enumerate(values):
                    lbl = QLabel(str(value))
                    if col == 0:
                        lbl.setStyleSheet("color: #eaeaea; font-weight: bold;")
                    grid.addWidget(lbl, row, col)

            grid.setColumnStretch(len(headers), 1)
            scroll.setWidget(content)
            return scroll

        # Encounter tabs (this fight only), one per category
        for label, columns_fn in categories:
            columns = columns_fn(self.characters, None)
            tab = _build_table_widget(
                self.characters, None, columns, is_players_tab=False
            )
            tabs.addTab(tab, f"Encounter - {label}")

        # Player tabs (lifetime aggregates), one per category
        stats_by_name = self._compute_player_log_stats()
        players = [c for c in self.characters if c.get("_is_player")]
        for label, columns_fn in categories:
            columns = columns_fn(players, stats_by_name)
            tab = _build_table_widget(
                players, stats_by_name, columns, is_players_tab=True
            )
            tabs.addTab(tab, f"Players - {label}")

        outer.addWidget(tabs)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        outer.addWidget(close_btn)

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
            filter_category_tree(
                category_items,
                query.strip().lower(),
                lambda rule, q: rule.matches(q),
            )

        search_box.textChanged.connect(apply_filter)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        outer.addWidget(close_btn)

        dlg.exec()

    _CONDITION_COLORS: dict[str, str] = {
        "Poisoned": "#1a5c1a",
        "Frightened": "#7a3d00",
        "Charmed": "#5c1a7a",
        "Blinded": "#3a3a3a",
        "Concentrating": "#1a3a7a",
        "Paralyzed": "#7a1a1a",
        "Stunned": "#7a1a1a",
        "Grappled": "#5c4a00",
        "Prone": "#5c4a00",
    }

    def _show_condition_info(self, condition_name: str):
        rule = ConditionRule.from_name(condition_name)
        if rule is None:
            return
        self._show_rule_popup(condition_name, rule.heading, rule.description)

    # Cover grades share a single "Cover" entry in rules.json
    _VISIBILITY_RULE_NAMES = {
        "Half Cover": "Cover",
        "Three-Quarters Cover": "Cover",
        "Total Cover": "Cover",
    }

    def _visibility_rule(self, visibility_name: str) -> Rule | None:
        rule_name = self._VISIBILITY_RULE_NAMES.get(visibility_name, visibility_name)
        if not hasattr(self, "_rules_cache"):
            self._rules_cache: list[Rule] = load_rules()
        return next((r for r in self._rules_cache if r.name == rule_name), None)

    def _show_visibility_info(self, visibility_name: str):
        rule = self._visibility_rule(visibility_name)
        if rule is None:
            return
        self._show_rule_popup(
            visibility_name, f"{rule.name} [{rule.category}]", rule.body
        )

    def _show_rule_popup(self, title: str, heading: str, body: str):
        dlg = QDialog(self._window)
        dlg.setWindowTitle(title)
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
