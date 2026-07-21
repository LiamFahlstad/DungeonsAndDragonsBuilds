"""Cards/rendering mixin for CombatAppQt."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import ConditionRule


class CardsMixin:
    """Mixin for card rendering and display."""

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

    def _card_state_flags(self, char: dict) -> tuple[bool, bool, bool]:
        """Return (is_source, is_active/turn, is_target) for a combatant card."""
        is_source = char is self.selected_character
        is_active = (
            self.phase == "COMBAT"
            and self.initiative_order
            and self.initiative_order[self.current_turn_idx] is char
        )
        is_target = char is self.target_character
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
        hp = char["hp"]
        death_state = self._char_death_state(char)
        is_dead = death_state == "dead"
        is_dying = death_state == "dying"
        is_stabilized = death_state == "stabilized"

        card = QFrame()
        card.setObjectName("combatantCard")
        self._apply_card_state_properties(card, char, death_state)
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

        if is_dying:
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

        # --- Visibility states ---
        visibility_states = char.get("visibility_states", [])
        if visibility_states:
            vis_row = QHBoxLayout()
            vis_row.setSpacing(3)
            vis_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
            for vis in visibility_states:
                # Use a blue/cyan color for visibility states
                if self._visibility_rule(vis) is not None:
                    vis_badge = QPushButton(vis)
                    vis_badge.setFlat(True)
                    vis_badge.setStyleSheet(
                        "QPushButton { background-color: #1a5c7a; color: #ffffff;"
                        " border-radius: 3px; padding: 1px 4px; font-size: 10px;"
                        " border: none; cursor: pointer; }"
                        "QPushButton:hover { background-color: #1a5c7acc; }"
                    )
                    vis_badge.setCursor(Qt.CursorShape.PointingHandCursor)
                    vis_badge.clicked.connect(
                        lambda _=False, v=vis: self._show_visibility_info(v)
                    )
                else:
                    vis_badge = QLabel(vis)
                    vis_badge.setStyleSheet(
                        "background-color: #1a5c7a; color: #ffffff;"
                        " border-radius: 3px; padding: 1px 4px; font-size: 10px;"
                    )
                vis_row.addWidget(vis_badge)
            vis_row.addStretch()
            layout.addLayout(vis_row)

        # --- Spell slots ---
        slots = {k: v for k, v in (char.get("spell_slots") or {}).items() if v > 0}
        if slots:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #0f3460;")
            layout.addWidget(sep)
            slots_header = QLabel("Slots:")
            slots_header.setStyleSheet(
                "color: #c9a84c; font-size: 10px; font-weight: bold;"
            )
            layout.addWidget(slots_header)
            slots_text = "  ".join(
                f"LV{lv}({cnt})" for lv, cnt in sorted(slots.items())
            )
            slots_lbl = QLabel(slots_text)
            slots_lbl.setStyleSheet("color: #a0c4ff; font-size: 11px;")
            layout.addWidget(slots_lbl)

        # --- Active spells (time bars) ---
        active_spells = char.get("active_spells") or []
        if active_spells:
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet("color: #0f3460;")
            layout.addWidget(sep2)
            spells_header = QLabel("Active Spells:")
            spells_header.setStyleSheet(
                "color: #c9a84c; font-size: 10px; font-weight: bold;"
            )
            layout.addWidget(spells_header)
            for entry in active_spells:
                spell_name_row = QHBoxLayout()
                spell_name_row.setSpacing(4)
                name_row = QLabel(entry["name"])
                name_row.setStyleSheet("color: #a0c4ff; font-size: 10px;")
                spell_name_row.addWidget(name_row, stretch=1)
                remove_spell_btn = QPushButton("×")
                remove_spell_btn.setFixedSize(16, 16)
                remove_spell_btn.setToolTip(f"Dismiss {entry['name']}")
                remove_spell_btn.setStyleSheet(
                    "QPushButton { background-color: #5c1a1a; color: #ffffff;"
                    " border: none; border-radius: 3px; font-size: 10px; padding: 0px; }"
                    "QPushButton:hover { background-color: #7a2a2a; }"
                )
                remove_spell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                remove_spell_btn.clicked.connect(
                    lambda _=False, c=char, e=entry: self._remove_active_spell(c, e)
                )
                spell_name_row.addWidget(remove_spell_btn)
                layout.addLayout(spell_name_row)
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

        # --- Action economy used this round ---
        action_uses = {
            k: v for k, v in (char.get("action_uses") or {}).items() if v > 0
        }
        if action_uses:
            sep3 = QFrame()
            sep3.setFrameShape(QFrame.Shape.HLine)
            sep3.setStyleSheet("color: #0f3460;")
            layout.addWidget(sep3)
            actions_header = QLabel("Used:")
            actions_header.setStyleSheet(
                "color: #c9a84c; font-size: 10px; font-weight: bold;"
            )
            layout.addWidget(actions_header)
            actions_lbl = QLabel(self._format_action_uses(action_uses))
            actions_lbl.setStyleSheet("color: #a0c4ff; font-size: 11px;")
            actions_lbl.setWordWrap(True)
            layout.addWidget(actions_lbl)

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
                chunk = entries[row_idx * 3 : row_idx * 3 + 3]
                if chunk:
                    if chunk[0][3]:  # has saving throws
                        row_text = "  ".join(
                            f"{abbr} {m:+d}/{s:+d}" for abbr, m, s, _ in chunk
                        )
                    else:
                        row_text = "  ".join(f"{abbr} {m:+d}" for abbr, m, *_ in chunk)
                    row_lbl = QLabel(row_text)
                    row_lbl.setStyleSheet(
                        "font-family: monospace; font-size: 10px; color: #a0a0b0;"
                    )
                    layout.addWidget(row_lbl)

        # --- Click to select: left = source, right = target ---
        card.mousePressEvent = lambda event, c=char: (
            self._select_target_character(c)
            if event.button() == Qt.MouseButton.RightButton
            else self._select_character(c)
        )
        for child in card.findChildren(QWidget):
            if not isinstance(child, QPushButton):
                child.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
                )

        return card
