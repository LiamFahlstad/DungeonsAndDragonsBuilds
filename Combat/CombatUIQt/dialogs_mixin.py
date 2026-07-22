"""Dialogs mixin for CombatAppQt."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

import Definitions
from Combat.Definitions import ConditionRule
from Combat.Rules import Rule, group_by_category, load_rules

from .styles import QSS


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


def _monster_type_text(char: dict) -> str:
    parts = []
    if char.get("size"):
        parts.append(_display(char["size"]))
    if char.get("monster_type"):
        parts.append(char["monster_type"])
    text = " ".join(parts)
    if char.get("alignment"):
        alignment_text = _display(char["alignment"])
        text = f"{text}, {alignment_text}" if text else alignment_text
    return text


def _speed_text(char: dict) -> str:
    parts = []
    if char.get("speed_ground_ft") is not None:
        parts.append(f"{char['speed_ground_ft']} ft.")
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


class DialogsMixin:
    """Mixin for dialog windows."""

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
                add_field(
                    "Spell Slots", "  ".join(f"L{k}×{v}" for k, v in active.items())
                )

        scores = char.get("Ability Scores", {})
        saves = char.get("Saving Throws", {})
        if scores:
            add_divider()
            add_header("Ability Scores")
            td = "border:1px solid #0f3460;text-align:center;padding:2px 7px;"
            tds = "border:1px solid #0f3460;text-align:center;padding:2px 7px;color:#a0a0b0;font-size:11px;"
            tdt = "border:1px solid #0f3460;border-top:2px solid #0f3460;text-align:center;padding:2px 7px;color:#a0a0b0;font-size:11px;"
            cells_h = cells_v = cells_m = cells_s = ""
            for key, val in scores.items():
                mod = (val - 10) // 2
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
                add_field(
                    "Class",
                    ", ".join(
                        f"{cls} {lvl}" for cls, lvl in char["class_levels"].items()
                    ),
                )
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
                    has_exp = sb.has_expertise_in_skill(skill)
                    is_prof = sb.is_proficient_in_skill(skill)
                    if has_exp:
                        name_html = f"<b>{skill.value}</b>"
                        prof_html = (
                            f"<span style='color:#d4a747;font-weight:bold'>Exp</span>"
                        )
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
                    add_field(
                        "Spell DC",
                        "  ".join(
                            f"DC {dc} ({ab.short_name})" for ab, (dc, _) in seen.items()
                        ),
                    )
                    add_field(
                        "Spell Attack",
                        "  ".join(
                            f"{atk:+} ({ab.short_name})"
                            for ab, (_, atk) in seen.items()
                        ),
                    )

            # Spells as expandable items grouped by level
            spell_objects_map = char.get("_spell_objects", {})
            if spells_with_level:
                add_divider()
                add_header("Spells")
                current_level = -1
                for spell_name, level, _ in sorted(
                    spells_with_level, key=lambda s: (s[1], s[0])
                ):
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
                        if spell_obj.additional_ruling:
                            ruling_lbl = QLabel(
                                f"<span style='color:#c9a84c'>Ruling:</span> "
                                f"<span style='color:#c0c0c0'>{spell_obj.additional_ruling}</span>"
                            )
                            ruling_lbl.setTextFormat(Qt.TextFormat.RichText)
                            ruling_lbl.setWordWrap(True)
                            ruling_lbl.setStyleSheet("font-size: 11px;")
                            swl.addWidget(ruling_lbl)
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

                    prof_str = (
                        "Proficient"
                        if weapon.player_is_proficient
                        else "Not proficient"
                    )
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
                        mark = (
                            "✓" if getattr(weapon, "player_has_mastery", False) else "✗"
                        )
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
                        prop_header_lbl.setStyleSheet(
                            "color: #a0a0b0; font-size: 11px;"
                        )
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
                            if desc_text is None:
                                lay.addWidget(QLabel(f"• {feat_name}"))
                                continue
                            fw = QWidget()
                            fwl = QVBoxLayout(fw)
                            fwl.setContentsMargins(16, 2, 0, 4)
                            fwl.setSpacing(2)
                            origin = getattr(feat, "origin", "")
                            if origin:
                                orig_lbl = QLabel(
                                    f"<i style='color:#a0a0b0'>{origin}</i>"
                                )
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
            type_text = _monster_type_text(char)
            if type_text:
                add_field("Type", type_text)
            for key, label in [
                ("cr", "CR"),
            ]:
                if char.get(key):
                    add_field(label, char[key])
            speed_text = _speed_text(char)
            if speed_text:
                add_field("Speed", speed_text)
            for key, label in [
                ("hp_formula", "Hit Dice"),
                ("senses", "Senses"),
                ("languages", "Languages"),
            ]:
                if char.get(key):
                    add_field(label, char[key])

            if char.get("skills"):
                add_header("Skills")
                td = "border:1px solid #0f3460;padding:2px 8px;"
                tdr = f"{td}text-align:right;"
                rows = "".join(
                    f"<tr><td style='{td}'>{_display(k)}</td><td style='{tdr}'>{v:+}</td></tr>"
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
            ]:
                entries = char.get(key, [])
                if entries:
                    add_field(label, "; ".join(_damage_entry_text(e) for e in entries))

            if char.get("condition_immunities"):
                add_field(
                    "Condition Immunities",
                    ", ".join(_display(c) for c in char["condition_immunities"]),
                )

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
                        name, desc = _ability_entry(ab)
                        add_ability(name, desc)

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(30)
        close_btn.clicked.connect(dlg.accept)
        outer.addWidget(close_btn)

        dlg.exec()

    def _show_statistics(self):
        """Display battle statistics for every combatant."""
        dlg = QDialog(self._window)
        dlg.setWindowTitle("Statistics")
        dlg.setMinimumSize(760, 400)
        dlg.setStyleSheet(QSS)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout(content)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(6)

        headers = [
            "Name",
            "Dmg Dealt",
            "Dmg Taken",
            "Heal Done",
            "Heal Received",
            "Knockouts",
            "Times Downed",
            "Deaths",
            "Status",
        ]
        for col, text in enumerate(headers):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #c9a84c; font-weight: bold;")
            grid.addWidget(lbl, 0, col)

        for row, char in enumerate(self.characters, start=1):
            stats = char.get("stats") or {}
            status = self._char_death_state(char)
            values = [
                char.get("name", ""),
                stats.get("damage_dealt", 0),
                stats.get("damage_taken", 0),
                stats.get("healing_done", 0),
                stats.get("healing_received", 0),
                stats.get("knockouts", 0),
                stats.get("times_downed", 0),
                stats.get("deaths", 0),
                status,
            ]
            for col, value in enumerate(values):
                lbl = QLabel(str(value))
                if col == 0:
                    lbl.setStyleSheet("color: #eaeaea; font-weight: bold;")
                grid.addWidget(lbl, row, col)

        grid.setColumnStretch(len(headers), 1)
        scroll.setWidget(content)
        outer.addWidget(scroll)

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

    # Condition badge color map
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
