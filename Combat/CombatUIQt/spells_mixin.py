"""Spells mixin for CombatAppQt."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from Combat.Definitions import Action, Condition
from .stats import _default_stats, spell_slots_used_key
from .styles import QSS


class SpellsMixin:
    """Mixin for spell-related methods."""

    def _cast_spell_slot_level(self, level: int):
        if not self.selected_character:
            return
        if self.selected_character["spell_slots"].get(level, 0) <= 0:
            return
        old = self.selected_character["spell_slots"][level]
        self.selected_character["spell_slots"][level] = max(old - 1, 0)
        self.selected_character.setdefault("stats", _default_stats())
        self.selected_character["stats"]["spell_slots_used"] = (
            self.selected_character["stats"].get("spell_slots_used", 0) + 1
        )
        level_key = spell_slots_used_key(level)
        self.selected_character["stats"][level_key] = (
            self.selected_character["stats"].get(level_key, 0) + 1
        )
        self.history.append((Action.REMOVE_SPELL_SLOT, level))
        self._log_event(
            f"{self.selected_character['name']} uses a Level {level} spell slot",
            character=self.selected_character["name"],
            action=Action.REMOVE_SPELL_SLOT,
            value=level,
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
            f"{self.selected_character['name']} regains a Level {level} spell slot",
            character=self.selected_character["name"],
            action=Action.ADD_SPELL_SLOT,
            value=level,
        )
        self._refresh_selected_card()

    def _clear_concentration_if_unused(self, char: dict):
        """Remove Concentrating if no remaining active spell on char still needs it."""
        if any(e.get("concentration") for e in char.get("active_spells") or []):
            return
        conditions = char.get("conditions", [])
        if Condition.CONCENTRATING.value in conditions:
            conditions.remove(Condition.CONCENTRATING.value)

    def _tick_active_spells(self):
        """Deduct 6 seconds (one round) from every combatant's active spell timers,
        expiring and logging any that reach zero, and dropping Concentrating if its
        spell expired."""
        for char in self.characters:
            active_spells = char.get("active_spells")
            if not active_spells:
                continue
            remaining = []
            expired_concentration = False
            for entry in active_spells:
                entry["time_left"] = max(entry["time_left"] - 6, 0)
                if entry["time_left"] > 0:
                    remaining.append(entry)
                else:
                    self._log_event(
                        f"{char['name']}'s {entry['name']} expires", note_turn=False
                    )
                    if entry.get("concentration"):
                        expired_concentration = True
            char["active_spells"] = remaining
            if expired_concentration:
                self._clear_concentration_if_unused(char)
        self._rebuild_cards()

    def _remove_active_spell(self, char: dict, entry: dict):
        """Manually dismiss an active spell before its duration timer runs out."""
        active_spells = char.get("active_spells") or []
        if entry not in active_spells:
            return
        active_spells.remove(entry)
        self._log_event(f"{char['name']}'s {entry['name']} ends early")
        if entry.get("concentration"):
            self._clear_concentration_if_unused(char)
        self._rebuild_card(char)

    def _show_cast_spell_dialog(self):
        """Search the spell list (like Rules) and cast a spell on the selected combatant."""
        if not self.selected_character:
            return

        from CharacterContent.Spells.SpellFactory import SpellFactory

        if not hasattr(self, "_spells_cache"):
            self._spells_cache = sorted(
                SpellFactory.all_spells(), key=lambda s: (s.level, s.name)
            )
        spells = self._spells_cache

        dlg = QDialog(self._window)
        dlg.setWindowTitle(f"Cast Spell — {self.selected_character['name']}")
        dlg.setMinimumSize(760, 560)
        dlg.setStyleSheet(QSS)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(8)

        search_box = QLineEdit()
        search_box.setPlaceholderText("Search spells…")
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

        def level_label(level: int) -> str:
            return "Cantrips" if level == 0 else f"Level {level}"

        category_items: dict[str, QTreeWidgetItem] = {}
        for spell in spells:
            category = level_label(spell.level)
            cat_item = category_items.get(category)
            if cat_item is None:
                cat_item = QTreeWidgetItem([category])
                cat_item.setFirstColumnSpanned(True)
                tree.addTopLevelItem(cat_item)
                category_items[category] = cat_item
            spell_item = QTreeWidgetItem([spell.name])
            spell_item.setData(0, Qt.ItemDataRole.UserRole, spell)
            cat_item.addChild(spell_item)

        selected_spell: dict[str, object] = {"spell": None}

        def show_spell(spell):
            tags = []
            if spell.is_concentration:
                tags.append("Concentration")
            if spell.is_ritual:
                tags.append("Ritual")
            tag_text = f" [{', '.join(tags)}]" if tags else ""
            detail.setHtml(
                f"<b style='color:#c9a84c; font-size:14px;'>{spell.name}</b>{tag_text}"
                f"<br><span style='color:#a0a0b0;'>{level_label(spell.level)} · {spell.school}</span>"
                f"<br><br><b>Casting Time:</b> {spell.casting_time}"
                f"<br><b>Range:</b> {spell.range}"
                f"<br><b>Components:</b> {spell.components}"
                f"<br><b>Duration:</b> {spell.duration}"
                f"<br><br>{spell.description.replace(chr(10) + chr(10), '<br><br>')}"
            )
            selected_spell["spell"] = spell
            cast_btn.setEnabled(True)
            condition_btn.setEnabled(True)

        def on_selection_changed():
            items = tree.selectedItems()
            if not items:
                return
            spell = items[0].data(0, Qt.ItemDataRole.UserRole)
            if spell is not None:
                show_spell(spell)

        tree.itemSelectionChanged.connect(on_selection_changed)

        def apply_filter(query: str):
            query = query.strip().lower()
            for category, cat_item in category_items.items():
                any_visible = False
                for i in range(cat_item.childCount()):
                    child = cat_item.child(i)
                    spell = child.data(0, Qt.ItemDataRole.UserRole)
                    visible = query in spell.name.lower()
                    child.setHidden(not visible)
                    any_visible = any_visible or visible
                cat_item.setHidden(not any_visible)
                if query:
                    cat_item.setExpanded(any_visible)

        search_box.textChanged.connect(apply_filter)

        btn_row = QHBoxLayout()
        cast_btn = QPushButton("Cast")
        cast_btn.setEnabled(False)

        def do_cast():
            spell = selected_spell["spell"]
            if spell is None:
                return
            self._apply_cast_spell(spell)
            dlg.accept()

        cast_btn.clicked.connect(do_cast)

        condition_btn = QPushButton("Apply as Condition")
        condition_btn.setEnabled(False)

        def do_apply_condition():
            spell = selected_spell["spell"]
            if spell is None:
                return
            self._apply_spell_as_condition(spell)
            dlg.accept()

        condition_btn.clicked.connect(do_apply_condition)

        close_btn2 = QPushButton("Close")
        close_btn2.clicked.connect(dlg.reject)
        btn_row.addWidget(cast_btn)
        btn_row.addWidget(condition_btn)
        btn_row.addWidget(close_btn2)
        outer.addLayout(btn_row)

        dlg.exec()

    def _apply_cast_spell(self, spell):
        """Apply a cast spell to the selected combatant: log it, auto-apply Concentrating,
        and start a duration timer (shown as a time bar) unless the spell is instantaneous."""
        char = self.selected_character
        if char is None:
            return

        self._log_event(f"{char['name']} casts {spell.name}")

        if spell.is_concentration:
            # Self-applied — the caster is always the source of their own concentration.
            self._add_condition_to(char, Condition.CONCENTRATING.value, source=char)

        duration = spell.duration_seconds
        if duration:
            char.setdefault("active_spells", []).append(
                {
                    "name": spell.name,
                    "time_left": duration,
                    "duration": duration,
                    "concentration": spell.is_concentration,
                }
            )

        self._refresh_selected_card()

    def _apply_spell_as_condition(self, spell):
        """Add a spell's name as a condition badge on the selected combatant,
        with the spell's full description available as a hover tooltip."""
        char = self.selected_character
        if char is None:
            return

        from CharacterContent.Spells.SpellFactory import Spell

        # Build tooltip HTML from the spell details
        tags = []
        if spell.is_concentration:
            tags.append("Concentration")
        if spell.is_ritual:
            tags.append("Ritual")
        tag_text = f" [{', '.join(tags)}]" if tags else ""

        def level_label(level: int) -> str:
            return "Cantrips" if level == 0 else f"Level {level}"

        tooltip_html = (
            f"<b style='color:#c9a84c; font-size:14px;'>{spell.name}</b>{tag_text}"
            f"<br><span style='color:#a0a0b0;'>{level_label(spell.level)} · {spell.school}</span>"
            f"<br><br><b>Casting Time:</b> {spell.casting_time}"
            f"<br><b>Range:</b> {spell.range}"
            f"<br><b>Components:</b> {spell.components}"
            f"<br><b>Duration:</b> {spell.duration}"
            f"<br><br>{spell.description.replace(chr(10) + chr(10), '<br><br>')}"
        )

        # Store the tooltip description and the school-of-magic badge color
        char.setdefault("spell_condition_descriptions", {})[spell.name] = tooltip_html
        char.setdefault("spell_condition_colors", {})[spell.name] = Spell.get_school_color(
            spell.school
        )

        # Add the spell name as a condition (self-applied, same as this method's
        # existing single-combatant scope)
        self._add_condition_to(char, spell.name, source=char)
