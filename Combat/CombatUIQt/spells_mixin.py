"""Spells mixin for CombatAppQt."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from Model.Content.Feature import FeatureTarget
from Combat.Definitions import Action, CombatStatus
from .stats import _default_stats, increment_named_stat, spell_slots_used_key
from .styles import QSS
from .state import CombatWindowState
from .undo import undoable
from .tree_filter import filter_category_tree, first_visible_item


def spell_slot_choices(char: dict, spell_level: int) -> list[tuple[str, int | None]]:
    """What char can pay for a spell of spell_level with, as (label, slot
    level), cheapest first: its slots of that level or higher that have any
    left, then casting without one (a ritual, an item, a feature). A cantrip
    needs no slot, and neither does a caster whose slots aren't tracked."""
    if spell_level == 0:
        return [("Cantrip: no slot", None)]
    slots = char.get("spell_slots") or {}
    if not slots:
        return [("No slots tracked", None)]
    paid = [
        (f"Level {level} slot ({count} left)", level)
        for level, count in sorted(slots.items())
        if level >= spell_level and count > 0
    ]
    return paid + [("No slot (ritual, item or feature)", None)]


class SpellsMixin(CombatWindowState):
    """Mixin for spell-related methods."""

    @undoable
    def _cast_spell_slot_level(self, level: int):
        if not self.selected_character:
            self._show_status("Nothing spent: left-click a card to pick a source.")
            return
        if self.selected_character["spell_slots"].get(level, 0) <= 0:
            name = self.selected_character["name"]
            self._show_status(f"Nothing spent: {name} has no level {level} slots left.")
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
        self._log_event(
            f"{self.selected_character['name']} uses a Level {level} spell slot",
            character=self.selected_character["name"],
            action=Action.REMOVE_SPELL_SLOT,
            value=level,
        )
        self._refresh_selected_card()

    @undoable
    def _regain_spell_slot(self):
        if not self.selected_character:
            self._show_status("Nothing regained: left-click a card to pick a source.")
            return
        level = self.spell_combo.currentIndex() + 1
        old = self.selected_character["spell_slots"].get(level, 0)
        self.selected_character["spell_slots"][level] = old + 1
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
        char.pop("concentration_checks", None)
        conditions = char.get("conditions", [])
        if CombatStatus.CONCENTRATING.value in conditions:
            conditions.remove(CombatStatus.CONCENTRATING.value)

    def _end_concentration_spells(self, char: dict):
        """End every active spell on char that requires concentration. Call this
        whenever Concentrating is removed by any path other than the spell's own
        duration expiring — a manual shortcut, a failed save, incapacitation,
        knockout, or death — so the effect doesn't keep ticking on the card after
        the character has stopped concentrating on it."""
        active_spells = char.get("active_spells") or []
        ended = [e for e in active_spells if e.get("concentration")]
        if not ended:
            return
        char["active_spells"] = [e for e in active_spells if not e.get("concentration")]
        for entry in ended:
            self._log_event(
                f"{char['name']}'s {entry['name']} ends (concentration lost)",
                note_turn=False,
                character=char["name"],
            )

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
                        f"{char['name']}'s {entry['name']} expires",
                        note_turn=False,
                        character=char["name"],
                    )
                    if entry.get("concentration"):
                        expired_concentration = True
            char["active_spells"] = remaining
            if expired_concentration:
                self._clear_concentration_if_unused(char)
        self._rebuild_cards()

    @undoable
    def _remove_active_spell(self, char: dict, entry: dict):
        """Manually dismiss an active spell before its duration timer runs out."""
        active_spells = char.get("active_spells") or []
        if entry not in active_spells:
            return
        active_spells.remove(entry)
        self._log_event(
            f"{char['name']}'s {entry['name']} ends early", character=char["name"]
        )
        if entry.get("concentration"):
            self._clear_concentration_if_unused(char)
        self._rebuild_card(char)

    def _show_cast_spell_dialog(self):
        """Search the spell list (like Rules), the caster's own spells first,
        and cast one on the selected combatant, choosing the slot it uses.
        Enter in the search box picks the first match, and casts it once it's
        picked; double-clicking a spell casts it."""
        if not self.selected_character:
            self._show_status("No spell cast: left-click a card to pick a source.")
            return
        # Modal dialog: the selection can't change while it's open.
        character = self.selected_character

        from CharacterContent.Spells.SpellFactory import SpellFactory

        if not hasattr(self, "_spells_cache"):
            self._spells_cache = sorted(
                SpellFactory.all_spells(), key=lambda s: (s.level, s.name)
            )
        spells = self._spells_cache

        dlg = QDialog(self._window)
        dlg.setWindowTitle(f"Cast Spell — {character['name']}")
        dlg.setMinimumSize(760, 560)
        dlg.setStyleSheet(QSS)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(8)

        search_box = QLineEdit()
        search_box.setPlaceholderText("Search spells…")
        outer.addWidget(search_box)

        if self.target_characters:
            target_names = ", ".join(t["name"] for t in self.target_characters)
            target_text = f"Target(s): {target_names}"
        else:
            target_text = "Target(s): None selected — spells that require a target will be unavailable"
        target_info_lbl = QLabel(target_text)
        target_info_lbl.setObjectName("secondary")
        target_info_lbl.setWordWrap(True)
        outer.addWidget(target_info_lbl)

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

        def add_spell(category: str, spell):
            cat_item = category_items.get(category)
            if cat_item is None:
                cat_item = QTreeWidgetItem([category])
                cat_item.setFirstColumnSpanned(True)
                tree.addTopLevelItem(cat_item)
                category_items[category] = cat_item
            spell_item = QTreeWidgetItem([spell.name])
            spell_item.setData(0, Qt.ItemDataRole.UserRole, spell)
            cat_item.addChild(spell_item)

        own_category = f"{character['name']}'s Spells"
        for spell in sorted(
            character.get("_spell_objects", {}).values(),
            key=lambda s: (s.level, s.name),
        ):
            add_spell(own_category, spell)
        if own_category in category_items:
            category_items[own_category].setExpanded(True)
        for spell in spells:
            add_spell(level_label(spell.level), spell)

        selected_spell: dict[str, object] = {"spell": None}

        def show_spell(spell):
            tags = []
            if spell.is_concentration:
                tags.append("Concentration")
            if spell.is_ritual:
                tags.append("Ritual")
            tag_text = f" [{', '.join(tags)}]" if tags else ""

            target_text = (
                spell.target.value.replace("_", " ").title()
                if spell.target is not None
                else "None"
            )

            detail.setHtml(
                f"<b style='color:#c9a84c; font-size:14px;'>{spell.name}</b>{tag_text}"
                f"<br><span style='color:#a0a0b0;'>{level_label(spell.level)} · {spell.school}</span>"
                f"<br><br><b>Casting Time:</b> {spell.casting_time}"
                f"<br><b>Range:</b> {spell.range}"
                f"<br><b>Target:</b> {target_text}"
                f"<br><b>Components:</b> {spell.components}"
                f"<br><b>Duration:</b> {spell.duration}"
                f"<br><br>{spell.description.replace(chr(10) + chr(10), '<br><br>')}"
            )
            selected_spell["spell"] = spell

            if spell.target is None or spell.target == FeatureTarget.SELF:
                cast_btn.setEnabled(True)
                cast_btn.setToolTip(f"Cast on {character['name']} (self-applied)")
            elif self.target_characters:
                cast_btn.setEnabled(True)
                target_names = ", ".join(t["name"] for t in self.target_characters)
                cast_btn.setToolTip(
                    f"Cast on {target_names} (requires: {spell.target.value})"
                )
            elif spell.target == FeatureTarget.AREA:
                cast_btn.setEnabled(True)
                cast_btn.setToolTip(
                    "Cast into an area with no creatures marked "
                    "(select targets first to mark who is caught in it)"
                )
            else:
                cast_btn.setEnabled(False)
                cast_btn.setToolTip(
                    f"This spell requires a target ({spell.target.value}) — "
                    "select a target first (right-click a card)"
                )
            show_slot_choices(spell)

        def show_slot_choices(spell):
            choices = spell_slot_choices(character, spell.level)
            slot_combo.clear()
            for label, level in choices:
                slot_combo.addItem(label, level)
            slot_combo.setEnabled(len(choices) > 1)
            out_of_slots = (
                spell.level > 0
                and bool(character.get("spell_slots"))
                and len(choices) == 1
            )
            cast_btn.setText("Cast without a slot" if out_of_slots else "Cast")
            slot_warning.setText(
                f"No slot of level {spell.level} or higher left."
                if out_of_slots
                else ""
            )

        def on_selection_changed():
            items = tree.selectedItems()
            if not items:
                return
            spell = items[0].data(0, Qt.ItemDataRole.UserRole)
            if spell is not None:
                show_spell(spell)

        tree.itemSelectionChanged.connect(on_selection_changed)

        def apply_filter(query: str):
            filter_category_tree(
                category_items,
                query.strip().lower(),
                lambda spell, q: q in spell.name.lower(),
            )

        search_box.textChanged.connect(apply_filter)

        slot_row = QHBoxLayout()
        slot_row.addWidget(QLabel("Spell slot:"))
        slot_combo = QComboBox()
        slot_combo.setEnabled(False)
        slot_row.addWidget(slot_combo, stretch=1)
        slot_warning = QLabel("")
        slot_warning.setObjectName("statusLabel")
        slot_row.addWidget(slot_warning)
        outer.addLayout(slot_row)

        btn_row = QHBoxLayout()
        cast_btn = QPushButton("Cast")
        cast_btn.setEnabled(False)
        # Enter is search_entered's to decide, not the dialog's default button.
        cast_btn.setAutoDefault(False)

        def do_cast():
            spell = selected_spell["spell"]
            if spell is None:
                return
            self._apply_cast_spell(spell, slot_level=slot_combo.currentData())
            dlg.accept()

        cast_btn.clicked.connect(do_cast)

        def search_entered():
            current = tree.currentItem()
            is_picked = (
                current is not None
                and not current.isHidden()
                and current.data(0, Qt.ItemDataRole.UserRole) is not None
            )
            if not is_picked:
                match = first_visible_item(category_items)
                if match is not None:
                    tree.setCurrentItem(match)
            elif cast_btn.isEnabled():
                do_cast()

        def item_activated(item):
            is_spell = item.data(0, Qt.ItemDataRole.UserRole) is not None
            if is_spell and cast_btn.isEnabled():
                do_cast()

        search_box.returnPressed.connect(search_entered)
        tree.itemActivated.connect(item_activated)

        close_btn2 = QPushButton("Close")
        close_btn2.setAutoDefault(False)
        close_btn2.clicked.connect(dlg.reject)
        btn_row.addWidget(cast_btn)
        btn_row.addWidget(close_btn2)
        outer.addLayout(btn_row)

        dlg.exec()

    @undoable
    def _apply_cast_spell(self, spell, slot_level: int | None = None):
        """Cast a spell. The spell's own declared metadata decides what happens:
        spell.target decides who is affected (SELF/None always means the
        caster; AREA means whichever targets are selected, possibly none, since
        the caster alone tracks its duration and concentration; any other target
        type requires a target to be selected first),
        spell.casting_time_type logs the action-economy cost on the caster,
        spell.is_concentration breaks any prior concentration and marks the
        caster Concentrating (concentration always belongs to the caster, even
        when the spell's effect lands on a target), and spell.duration_seconds
        (if set) adds a ticking duration bar on every recipient. Every cast also
        adds a condition badge (with the description as a hover tooltip) on its
        recipient(s) and increments the caster's spells_cast stat. slot_level
        is the spell slot it uses, higher than the spell's level to upcast it;
        None uses no slot."""
        source = self.selected_character
        if source is None:
            self._show_status("No spell cast: left-click a card to pick a source.")
            return

        if spell.target is None or spell.target == FeatureTarget.SELF:
            recipients = [source]
        elif spell.target == FeatureTarget.AREA:
            recipients = list(self.target_characters)
        else:
            if not self.target_characters:
                self._show_status(
                    f"No spell cast: {spell.name} needs a target"
                    f" ({spell.target.value}). Right-click a card."
                )
                return
            recipients = self.target_characters

        # Usage bookkeeping on the caster
        source.setdefault("stats", _default_stats())
        source["stats"]["spells_cast"] = source["stats"].get("spells_cast", 0) + 1
        increment_named_stat(source["stats"], "spells_cast_by_name", spell.name)
        cast_value = {"spell_name": spell.name}
        upcast = f" at level {slot_level}" if (slot_level or 0) > spell.level else ""
        self._log_event(
            f"{source['name']} casts {spell.name}{upcast}",
            character=source["name"],
            action=Action.CAST_SPELL,
            value=cast_value,
        )
        if slot_level is not None:
            self._cast_spell_slot_level(slot_level)

        if spell.is_concentration:
            # Break any existing concentration spells before starting a new one
            active_spells = source.get("active_spells") or []
            remaining_spells = []
            for entry in active_spells:
                if entry.get("concentration"):
                    self._log_event(
                        f"{source['name']}'s {entry['name']} ends (concentration broken by casting {spell.name})",
                        character=source["name"],
                    )
                else:
                    remaining_spells.append(entry)
            source["active_spells"] = remaining_spells
            # A save still owed was for the spell that just ended.
            source.pop("concentration_checks", None)
            # Concentration always belongs to the caster, regardless of who the spell targets.
            self._add_condition_to(
                source, CombatStatus.CONCENTRATING.value, source=source
            )

        # Action economy: the caster spends the action, regardless of who it affects
        try:
            casting_time_type = spell.casting_time_type.value
            if casting_time_type in self.ACTION_ECONOMY_TYPES:
                self._add_action_use(casting_time_type)
        except ValueError:
            pass

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

        target_text = (
            spell.target.value.replace("_", " ").title()
            if spell.target is not None
            else "None"
        )

        tooltip_html = (
            f"<b style='color:#c9a84c; font-size:14px;'>{spell.name}</b>{tag_text}"
            f"<br><span style='color:#a0a0b0;'>{level_label(spell.level)} · {spell.school}</span>"
            f"<br><br><b>Casting Time:</b> {spell.casting_time}"
            f"<br><b>Range:</b> {spell.range}"
            f"<br><b>Target:</b> {target_text}"
            f"<br><b>Components:</b> {spell.components}"
            f"<br><b>Duration:</b> {spell.duration}"
            f"<br><br>{spell.description.replace(chr(10) + chr(10), '<br><br>')}"
        )
        badge_color = Spell.get_school_color(spell.school)

        # Duration -> a ticking bar, always tracked on the caster (source) regardless
        # of who the badge lands on — _tick_active_spells/_clear_concentration_if_unused
        # clear Concentrating off whichever character owns the expiring entry, and
        # Concentrating itself is only ever added to the caster.
        duration = spell.duration_seconds
        has_duration = bool(duration)

        # Store the tooltip description and badge color, and add the condition,
        # on every recipient (the caster for a self-cast, each target otherwise).
        for char in list(recipients):
            char.setdefault("spell_condition_descriptions", {})[
                spell.name
            ] = tooltip_html
            char.setdefault("spell_condition_colors", {})[spell.name] = badge_color
            self._add_condition_to(char, spell.name, source=source)

        if has_duration:
            source.setdefault("active_spells", []).append(
                {
                    "name": spell.name,
                    "time_left": duration,
                    "duration": duration,
                    "concentration": spell.is_concentration,
                }
            )

        self._refresh_selected_card()
