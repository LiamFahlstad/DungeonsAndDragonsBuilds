"""Cards/rendering mixin for CombatAppQt."""

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QMouseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import ConditionRule
from .dialogs_mixin import _damage_entry_text, _speed_text
from Core.Rules import ability_modifier
from .monster_actions import (
    LEGENDARY_ACTIONS_PER_ROUND,
    legendary_actions_left,
    legendary_resistances_left,
)
from .state import CombatWindowState
from .styles import QSS

# The conditions a card's quick menu offers, each one click to add or remove.
CARD_MENU_CONDITIONS = (
    "Blinded",
    "Charmed",
    "Frightened",
    "Grappled",
    "Incapacitated",
    "Poisoned",
    "Prone",
    "Restrained",
    "Stunned",
)


class _CombatantCard(QFrame):
    """A combatant's card. A left click selects it as the (only) source; a
    right click as the target, with Ctrl and Shift picking several targets as
    in a Windows list (see WindowMixin._select_target_character)."""

    def __init__(
        self,
        on_left_click: Callable[[], None],
        on_right_click: Callable[[bool, bool], None],
    ):
        super().__init__()
        self._on_left_click = on_left_click
        self._on_right_click = on_right_click

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        # `a0` is PyQt6's name for the event; an override must keep it.
        if a0 is None:
            return
        if a0.button() == Qt.MouseButton.RightButton:
            ctrl = bool(a0.modifiers() & Qt.KeyboardModifier.ControlModifier)
            shift = bool(a0.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            self._on_right_click(ctrl, shift)
        else:
            self._on_left_click()


class CardsMixin(CombatWindowState):
    """Mixin for card rendering and display."""

    def _rebuild_cards(self):
        """Remove all card widgets and recreate them from self.characters."""
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self._card_widgets.clear()

        for index, char in enumerate(self.characters):
            col = index // self.combatants_per_column
            row = index % self.combatants_per_column
            card = self._make_card(char)
            self._grid_layout.addWidget(card, row, col)
            self._card_widgets[id(char)] = card

        self._refresh_initiative_tracker()

    def _card_state_flags(self, char: dict) -> tuple[bool, bool, bool]:
        """Return (is_source, is_active/turn, is_target) for a combatant card."""
        is_source = char is self.selected_character
        is_active = any(char is c for c in self._current_turn_group())
        is_target = any(char is t for t in self.target_characters)
        return is_source, is_active, is_target

    def _apply_card_state_properties(self, card: QFrame, char: dict, death_state: str):
        """Set the dead/dying/stabilized/source/active/target combo properties on a card."""
        is_source, is_active, is_target = self._card_state_flags(char)
        card.setProperty("dead", "true" if death_state == "dead" else "false")
        card.setProperty("dying", "true" if death_state == "dying" else "false")
        card.setProperty(
            "stabilized", "true" if death_state == "stabilized" else "false"
        )
        card.setProperty(
            "selected",
            "true" if is_source and not is_active and not is_target else "false",
        )
        card.setProperty(
            "active",
            "true" if is_active and not is_source and not is_target else "false",
        )
        card.setProperty(
            "target",
            "true" if is_target and not is_source and not is_active else "false",
        )
        card.setProperty(
            "selected-active",
            "true" if is_source and is_active and not is_target else "false",
        )
        card.setProperty(
            "selected-target",
            "true" if is_source and is_target and not is_active else "false",
        )
        card.setProperty(
            "active-target",
            "true" if is_active and is_target and not is_source else "false",
        )
        card.setProperty(
            "selected-active-target",
            "true" if is_source and is_active and is_target else "false",
        )

    def _refresh_cards(self):
        """Update border/background of all cards to reflect selection, active-turn, and dead state."""
        for char in self.characters:
            card = self._card_widgets.get(id(char))
            if card is None:
                continue
            death_state = self._char_death_state(char)
            self._apply_card_state_properties(card, char, death_state)
            card.style().unpolish(card)
            card.style().polish(card)
        self._views_timer.start()

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
        self._views_timer.start()

    def _refresh_selected_card(self):
        """Rebuild only the selected card in-place."""
        if self.selected_character is not None:
            self._rebuild_card(self.selected_character)

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

    @staticmethod
    def _char_death_state(char: dict) -> str:
        """Return 'alive', 'dying', 'stabilized', or 'dead'. Only player
        characters, and monsters/NPCs that opt in with `death_saves`, make
        Death Saving Throws; any other combatant at 0 HP is dead. A summon
        whose HP isn't set yet (max HP 0, see TurnsMixin._hp_not_set) isn't."""
        if char["hp"] > 0 or char.get("max_hp", 1) <= 0:
            return "alive"
        if not (char.get("_is_player") or char.get("death_saves", False)):
            return "dead"
        if char.get("death_saves_fail", 0) >= 3:
            return "dead"
        if char.get("death_saves_success", 0) >= 3:
            return "stabilized"
        return "dying"

    def _format_action_uses(self, counts: dict) -> str:
        """Format e.g. {'Action': 2, 'Reaction': 1} as '2x Action, Reaction'."""
        parts = []
        for label in self.ACTION_ECONOMY_TYPES:
            n = counts.get(label, 0)
            if n <= 0:
                continue
            parts.append(f"{n}x {label}" if n > 1 else label)
        return ", ".join(parts)

    def _make_card(self, char: dict) -> QFrame:
        death_state = self._char_death_state(char)

        card = _CombatantCard(
            on_left_click=lambda: self._select_character(char),
            on_right_click=lambda ctrl, shift: self._card_right_clicked(
                char, ctrl, shift
            ),
        )
        card.setObjectName("combatantCard")
        self._apply_card_state_properties(card, char, death_state)
        card.setFixedWidth(220)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        self._add_card_name_and_death_saves(layout, char, death_state)
        self._add_saved_toggle(layout, char)
        self._add_concentration_checks(layout, char)
        layout.addLayout(_hp_row(char))
        layout.addWidget(_ac_speed_label(char))
        self._add_condition_badges(layout, char)
        self._add_visibility_badges(layout, char)
        _add_defenses(layout, char)
        _add_monster_counters(layout, char)
        _add_spell_slots(layout, char)
        _add_timed_entries(
            layout,
            char,
            "active_spells",
            "Active Spells:",
            lambda c, e: self._remove_active_spell(c, e),
        )
        _add_timed_entries(
            layout,
            char,
            "active_features",
            "Active Features:",
            lambda c, e: self._remove_active_feature(c, e),
        )
        _add_timed_entries(
            layout,
            char,
            "timed_conditions",
            "Timed Conditions:",
            lambda c, e: self._remove_condition_from(c, e["name"]),
        )
        self._add_action_uses(layout, char)
        _add_ability_rows(layout, char)

        # Clicks select (see _CombatantCard): children let them through.
        for child in card.findChildren(QWidget):
            if not isinstance(child, QPushButton):
                child.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
                )

        return card

    def _add_card_name_and_death_saves(
        self, layout: QVBoxLayout, char: dict, death_state: str
    ):
        """The name (marked by death state), then for a combatant at 0 HP its
        death-save pips, and while still dying its Fail/Save buttons."""
        prefix, name_style = _DEATH_STATE_NAME_STYLES.get(death_state, ("", ""))
        name_lbl = QLabel(prefix + char["name"])
        name_lbl.setObjectName("cardName")
        if name_style:
            name_lbl.setStyleSheet(name_style)
        layout.addWidget(name_lbl)

        if death_state in ("dying", "stabilized"):
            fail = char.get("death_saves_fail", 0)
            success = char.get("death_saves_success", 0)
            pips_lbl = QLabel(
                f"<span style='color:#c04040'>{'●' * fail}{'○' * (3 - fail)}</span>"
                f"  "
                f"<span style='color:#40c040'>{'●' * success}{'○' * (3 - success)}</span>"
            )
            pips_lbl.setTextFormat(Qt.TextFormat.RichText)
            pips_lbl.setStyleSheet("font-size: 11px; letter-spacing: 2px;")
            layout.addWidget(pips_lbl)

        if death_state == "dying":
            btn_row = QHBoxLayout()
            btn_row.setSpacing(4)
            fail_btn = QPushButton("✗ Fail")
            fail_btn.setObjectName("deathFailBtn")
            fail_btn.setFixedHeight(24)
            fail_btn.clicked.connect(
                lambda _=False, c=char: self._apply_failed_death_save(c)
            )
            save_btn = QPushButton("✓ Save")
            save_btn.setObjectName("deathSuccessBtn")
            save_btn.setFixedHeight(24)
            save_btn.clicked.connect(
                lambda _=False, c=char: self._apply_success_death_save(c)
            )
            btn_row.addWidget(fail_btn)
            btn_row.addWidget(save_btn)
            layout.addLayout(btn_row)

        if death_state == "dead":
            revive_btn = QPushButton("✚ Revive")
            revive_btn.setObjectName("reviveBtn")
            revive_btn.setFixedHeight(24)
            revive_btn.setToolTip("Bring back with 1 HP (Revivify, Raise Dead, ...)")
            revive_btn.clicked.connect(lambda _=False, c=char: self._revive(c))
            layout.addWidget(revive_btn)

    def _add_saved_toggle(self, layout: QVBoxLayout, char: dict):
        """With several targets, whether this one saved, for half damage (one
        target only needs the panel's ½ Saved button)."""
        if len(self.target_characters) < 2 or not any(
            char is t for t in self.target_characters
        ):
            return
        toggle = QPushButton("½ Saved")
        toggle.setObjectName("savedToggle")
        toggle.setCheckable(True)
        toggle.setChecked(any(char is s for s in self._saved_targets))
        toggle.setFixedHeight(22)
        toggle.setToolTip("This target saved: it takes half of the next damage")
        toggle.clicked.connect(lambda _=False, c=char: self._toggle_saved(c))
        layout.addWidget(toggle)

    def _add_concentration_checks(self, layout: QVBoxLayout, char: dict):
        """Each Concentration save char owes: roll it, or say how it went."""
        for dc in char.get("concentration_checks", []):
            label = QLabel(f"DC {dc} CON ({self._con_save_mod(char):+d})")
            label.setObjectName("statusLabel")
            layout.addWidget(label)
            row = QHBoxLayout()
            row.setSpacing(4)
            roll_btn = QPushButton("Roll")
            roll_btn.clicked.connect(
                lambda _=False, c=char, d=dc: self._roll_concentration(c, d)
            )
            kept_btn = QPushButton("Kept")
            kept_btn.clicked.connect(
                lambda _=False, c=char, d=dc: self._settle_concentration(c, d, True)
            )
            lost_btn = QPushButton("Lost")
            lost_btn.clicked.connect(
                lambda _=False, c=char, d=dc: self._settle_concentration(c, d, False)
            )
            for button in (roll_btn, kept_btn, lost_btn):
                button.setObjectName("concentrationBtn")
                button.setFixedHeight(24)
                row.addWidget(button)
            layout.addLayout(row)

    def _card_right_clicked(self, char: dict, ctrl: bool, shift: bool):
        """Right-clicking picks targets; right-clicking the card that's already
        the only target opens its quick menu."""
        was_only_target = (
            not (ctrl or shift)
            and len(self.target_characters) == 1
            and self.target_characters[0] is char
        )
        self._select_target_character(char, ctrl=ctrl, shift=shift)
        if was_only_target:
            self._card_menu(char).popup(QCursor.pos())

    def _card_menu(self, char: dict) -> QMenu:
        """Damage, Heal and Temp HP for this target, and the common conditions
        a click away. It isn't modal: it closes with any click elsewhere."""
        menu = QMenu(self._window)
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.setStyleSheet(QSS)
        menu.addAction("Damage (D)", self._focus_damage_input)
        menu.addAction("Heal (H)", self._focus_heal_input)
        menu.addAction("Temp HP (T)", self._focus_temp_hp_input)
        menu.addSeparator()
        for cond in CARD_MENU_CONDITIONS:
            action = menu.addAction(cond)
            assert action is not None  # addAction with a text always makes one
            action.setCheckable(True)
            action.setChecked(cond in char["conditions"])
            action.triggered.connect(
                lambda _=False, c=char, name=cond: self._toggle_condition_on(c, name)
            )
        menu.addSeparator()
        menu.addAction("Custom... (Shift+C)", self._show_custom_condition_dialog)
        return menu

    def _toggle_condition_on(self, char: dict, cond: str):
        source = self.selected_character or self._current_turn_character()
        if cond in char["conditions"]:
            self._remove_condition_from(char, cond, source=source)
        else:
            self._add_condition_to(char, cond, source=source)

    def _add_condition_badges(self, layout: QVBoxLayout, char: dict):
        conditions = char.get("conditions", [])
        if not conditions:
            return
        cond_row = QHBoxLayout()
        cond_row.setSpacing(3)
        cond_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        for cond in conditions:
            cond_row.addWidget(self._condition_badge(char, cond))
        cond_row.addStretch()
        layout.addLayout(cond_row)

    def _condition_badge(self, char: dict, cond: str) -> QWidget:
        """A clickable badge when the condition has a rule or a description to
        show, a plain label otherwise; right-click removes it either way."""
        description, color = self._condition_description_and_color(char, cond)
        badge_color = color or self._CONDITION_COLORS.get(cond, "#7a5c00")
        has_rule = ConditionRule.from_name(cond) is not None
        badge: QWidget
        if has_rule or description:
            badge = QPushButton(cond)
            badge.setFlat(True)
            badge.setStyleSheet(_clickable_badge_style(badge_color))
            badge.setCursor(Qt.CursorShape.PointingHandCursor)
            if has_rule:
                badge.clicked.connect(
                    lambda _=False, c=cond: self._show_condition_info(c)
                )
            elif description:
                badge.clicked.connect(
                    lambda _=False, c=cond, d=description: self._show_rule_popup(
                        c, c, d
                    )
                )
        else:
            badge = QLabel(cond)
            badge.setStyleSheet(_badge_style(badge_color))
        if description:
            badge.setToolTip(description)
        badge.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        badge.customContextMenuRequested.connect(
            lambda _pos, c=char, cond=cond: self._remove_condition_from(c, cond)
        )
        return badge

    def _condition_description_and_color(
        self, char: dict, cond: str
    ) -> tuple[str | None, str | None]:
        """The tooltip text and badge color a spell or feature attached to this
        condition, if any."""
        description = (
            char.get("spell_condition_descriptions", {}).get(cond)
            or char.get("feature_condition_descriptions", {}).get(cond)
            or char.get("custom_condition_descriptions", {}).get(cond)
        )
        color = char.get("spell_condition_colors", {}).get(cond) or char.get(
            "feature_condition_colors", {}
        ).get(cond)
        if description is not None:
            return description, color
        # Feature-condition tooltips/colors are transient UI state, not
        # persisted to the player log — after replaying a saved session
        # (see logging_mixin._apply_replay_action) the condition name is
        # restored but the dicts above are empty. Reconstruct the tooltip
        # from a matching Feature object so the badge stays clickable/
        # removable exactly as it was before restart. The feature may
        # belong to a *different* character than the one wearing the
        # badge (e.g. Warding Flare is granted by its caster onto an
        # ally/enemy target) — search every loaded character for the
        # owner, not just this one, and build the tooltip (incl. "Uses
        # Left") from that owner's own state.
        for owner in self.characters:
            feature = next(
                (f for f in owner.get("_feature_objects", []) if f.name == cond),
                None,
            )
            if feature is not None:
                return (
                    self._feature_condition_tooltip(owner, feature),
                    color or "#4c7ac9",
                )
        return None, color

    def _add_visibility_badges(self, layout: QVBoxLayout, char: dict):
        visibility_states = char.get("visibility_states", [])
        if not visibility_states:
            return
        vis_row = QHBoxLayout()
        vis_row.setSpacing(3)
        vis_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        for vis in visibility_states:
            vis_badge: QWidget
            if self._visibility_rule(vis) is not None:
                vis_badge = QPushButton(vis)
                vis_badge.setFlat(True)
                vis_badge.setStyleSheet(_clickable_badge_style(_VISIBILITY_COLOR))
                vis_badge.setCursor(Qt.CursorShape.PointingHandCursor)
                vis_badge.clicked.connect(
                    lambda _=False, v=vis: self._show_visibility_info(v)
                )
            else:
                vis_badge = QLabel(vis)
                vis_badge.setStyleSheet(_badge_style(_VISIBILITY_COLOR))
            vis_row.addWidget(vis_badge)
        vis_row.addStretch()
        layout.addLayout(vis_row)

    def _add_action_uses(self, layout: QVBoxLayout, char: dict):
        """The action economy used this round."""
        action_uses = {
            k: v for k, v in (char.get("action_uses") or {}).items() if v > 0
        }
        if not action_uses:
            return
        layout.addWidget(_separator())
        layout.addWidget(_section_header("Used:"))
        actions_lbl = QLabel(self._format_action_uses(action_uses))
        actions_lbl.setStyleSheet("color: #a0c4ff; font-size: 11px;")
        actions_lbl.setWordWrap(True)
        layout.addWidget(actions_lbl)


_DEATH_STATE_NAME_STYLES: dict[str, tuple[str, str]] = {
    "dead": ("☠ ", "color: #555; font-weight: bold; font-size: 13px;"),
    "dying": ("💀 ", "color: #b070e0; font-weight: bold; font-size: 13px;"),
    "stabilized": ("😴 ", "color: #4a9080; font-weight: bold; font-size: 13px;"),
}

_VISIBILITY_COLOR = "#1a5c7a"


def _badge_style(color: str) -> str:
    return (
        f"background-color: {color}; color: #ffffff;"
        " border-radius: 3px; padding: 1px 4px; font-size: 10px;"
    )


def _clickable_badge_style(color: str) -> str:
    return (
        f"QPushButton {{ background-color: {color}; color: #ffffff;"
        " border-radius: 3px; padding: 1px 4px; font-size: 10px;"
        " border: none; cursor: pointer; }"
        f"QPushButton:hover {{ background-color: {color}cc; }}"
    )


def _separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setStyleSheet("color: #0f3460;")
    return sep


def _section_header(text: str) -> QLabel:
    header = QLabel(text)
    header.setStyleSheet("color: #c9a84c; font-size: 10px; font-weight: bold;")
    return header


def _hp_chunk_color(hp: int, max_hp: int) -> str:
    if hp <= 0:
        return "#555"
    if hp / max_hp <= 0.25:
        return "#e74c3c"
    if hp / max_hp <= 0.50:
        return "#e67e22"
    return "#2ecc71"


def _hp_row(char: dict) -> QHBoxLayout:
    """The HP bar, colored by how hurt the combatant is, plus any temp HP."""
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
    bar.setStyleSheet(
        f"QProgressBar::chunk {{ background-color: {_hp_chunk_color(hp, max_hp)};"
        " border-radius: 3px; }"
    )
    hp_row.addWidget(bar, stretch=1)

    if temp_hp and temp_hp > 0:
        temp_lbl = QLabel(f"(+{temp_hp} temp)")
        temp_lbl.setObjectName("secondary")
        temp_lbl.setStyleSheet("color: #5bc8f5; font-size: 10px;")
        hp_row.addWidget(temp_lbl)
    return hp_row


def _ac_speed_label(char: dict) -> QLabel:
    ac_speed_text = f"AC: {char['ac']}"
    speed_text = _speed_text(char)
    if speed_text:
        ac_speed_text = f"{ac_speed_text}   Speed: {speed_text}"
    ac_lbl = QLabel(ac_speed_text)
    ac_lbl.setObjectName("secondary")
    ac_lbl.setWordWrap(True)
    return ac_lbl


def _add_defenses(layout: QVBoxLayout, char: dict):
    """Damage vulnerabilities/resistances/immunities and condition immunities."""
    defense_rows = [
        ("Vulnerable", char.get("damage_vulnerabilities") or [], "#e74c3c"),
        ("Resist", char.get("damage_resistances") or [], "#4caf82"),
        ("Immune", char.get("damage_immunities") or [], "#4a9fc4"),
    ]
    defense_rows = [
        (label, entries, color) for label, entries, color in defense_rows if entries
    ]
    condition_immunities = char.get("condition_immunities")
    if not defense_rows and not condition_immunities:
        return
    layout.addWidget(_separator())
    for label, entries, color in defense_rows:
        text = "; ".join(_damage_entry_text(e) for e in entries)
        def_lbl = QLabel(f"{label}: {text}")
        def_lbl.setStyleSheet(f"color: {color}; font-size: 10px;")
        def_lbl.setWordWrap(True)
        layout.addWidget(def_lbl)
    if condition_immunities:
        cond_immune_text = ", ".join(
            c.value if hasattr(c, "value") else str(c) for c in condition_immunities
        )
        cond_immune_lbl = QLabel(f"Cond. Immune: {cond_immune_text}")
        cond_immune_lbl.setStyleSheet("color: #4a9fc4; font-size: 10px;")
        cond_immune_lbl.setWordWrap(True)
        layout.addWidget(cond_immune_lbl)


def _add_monster_counters(layout: QVBoxLayout, char: dict):
    """What a monster has left of what the fight uses up."""
    parts = []
    if char.get("legendary_actions"):
        left = legendary_actions_left(char)
        parts.append(f"Legendary {left}/{LEGENDARY_ACTIONS_PER_ROUND}")
    if char.get("legendary_resistances"):
        left = legendary_resistances_left(char)
        parts.append(f"Resist {left}/{char['legendary_resistances']}")
    spent = ", ".join(char.get("spent_abilities", {}))
    if not parts and not spent:
        return
    layout.addWidget(_separator())
    if parts:
        counters_lbl = QLabel("  ".join(parts))
        counters_lbl.setStyleSheet("color: #c9a84c; font-size: 11px;")
        layout.addWidget(counters_lbl)
    if spent:
        spent_lbl = QLabel(f"Spent: {spent}")
        spent_lbl.setStyleSheet("color: #e67e22; font-size: 10px;")
        spent_lbl.setWordWrap(True)
        layout.addWidget(spent_lbl)


def _add_spell_slots(layout: QVBoxLayout, char: dict):
    slots = {k: v for k, v in (char.get("spell_slots") or {}).items() if v > 0}
    if not slots:
        return
    layout.addWidget(_separator())
    layout.addWidget(_section_header("Slots:"))
    slots_lbl = QLabel("  ".join(f"LV{lv}({cnt})" for lv, cnt in sorted(slots.items())))
    slots_lbl.setStyleSheet("color: #a0c4ff; font-size: 11px;")
    layout.addWidget(slots_lbl)


def _add_timed_entries(
    layout: QVBoxLayout,
    char: dict,
    key: str,
    header: str,
    remove: Callable[[dict, dict], None],
):
    """Active spells, features or timed conditions (char[key]): each a name
    with a dismiss button, over a bar of the time it has left, or the turn it
    lasts until (entry["text"]) for one that ends on a turn."""
    entries = char.get(key) or []
    if not entries:
        return
    layout.addWidget(_separator())
    layout.addWidget(_section_header(header))
    for entry in entries:
        name_row = QHBoxLayout()
        name_row.setSpacing(4)
        name_lbl = QLabel(entry["name"])
        name_lbl.setStyleSheet("color: #a0c4ff; font-size: 10px;")
        name_row.addWidget(name_lbl, stretch=1)
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setToolTip(f"Dismiss {entry['name']}")
        remove_btn.setStyleSheet(
            "QPushButton { background-color: #5c1a1a; color: #ffffff;"
            " border: none; border-radius: 3px; font-size: 10px; padding: 0px; }"
            "QPushButton:hover { background-color: #7a2a2a; }"
        )
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(lambda _=False, c=char, e=entry: remove(c, e))
        name_row.addWidget(remove_btn)
        layout.addLayout(name_row)
        if "time_left" not in entry:
            until_lbl = QLabel(entry["text"])
            until_lbl.setStyleSheet("color: #a0a0b0; font-size: 10px;")
            until_lbl.setWordWrap(True)
            layout.addWidget(until_lbl)
            continue
        time_bar = QProgressBar()
        time_bar.setMinimum(0)
        time_bar.setMaximum(max(entry.get("duration", entry["time_left"]), 1))
        time_bar.setValue(max(entry["time_left"], 0))
        time_bar.setFormat(f"{entry['time_left']}s")
        time_bar.setTextVisible(True)
        time_bar.setFixedHeight(14)
        time_bar.setStyleSheet(
            "QProgressBar::chunk { background-color: #5ac8f5; border-radius: 3px; }"
        )
        layout.addWidget(time_bar)


def _add_ability_rows(layout: QVBoxLayout, char: dict):
    """Ability modifiers in two rows of three, each as mod/save when the
    combatant has saving throws."""
    ability_scores = char.get("Ability Scores") or {}
    saving_throws = char.get("Saving Throws") or {}
    if not ability_scores:
        return
    layout.addWidget(_separator())

    # Raw scores or already modifiers? Any value over 10 means raw scores.
    is_raw = any(v > 10 for v in ability_scores.values())
    entries = []
    for name, val in ability_scores.items():
        mod = ability_modifier(val) if is_raw else val
        # Saving throws are already modifiers — do not convert
        save = saving_throws.get(name, mod) if saving_throws else mod
        entries.append((name[:3].upper(), mod, save))

    for row_idx in range(2):
        chunk = entries[row_idx * 3 : row_idx * 3 + 3]
        if not chunk:
            continue
        if saving_throws:
            row_text = "  ".join(f"{abbr} {m:+d}/{s:+d}" for abbr, m, s in chunk)
        else:
            row_text = "  ".join(f"{abbr} {m:+d}" for abbr, m, _ in chunk)
        row_lbl = QLabel(row_text)
        row_lbl.setStyleSheet(
            "font-family: monospace; font-size: 10px; color: #a0a0b0;"
        )
        layout.addWidget(row_lbl)
