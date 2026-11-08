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
from Combat.PlayerCombatant import max_pact_slots
from Core.Definitions import Condition
from .effect_options import PactSlot, casting_time_cost, has_slots, spell_slot_choices
from .resources import spell_slot_lack
from .stats import _default_stats, increment_named_stat, spell_slots_used_key
from .styles import QSS
from .state import CombatWindowState
from .undo import undoable
from .tree_filter import filter_category_tree, first_visible_item


class SpellsMixin(CombatWindowState):
    """Mixin for spell-related methods."""

    @undoable
    def _cast_spell_slot_level(self, level: int):
        """Spend one of the source's slots of `level`: a Pact Magic slot for a
        PactSlot, else a spell slot, or a Pact Magic slot when no spell slot
        of that level is left (so the 1-9 keys work for a Warlock too)."""
        char = self.selected_character
        if not char:
            self._show_status("Nothing spent: left-click a card to pick a source.")
            return
        if self._spend_slot(char, level):
            self._refresh_selected_card()

    def _spend_slot(self, char: dict, level: int) -> bool:
        """Spend one of char's slots of `level`, as _cast_spell_slot_level
        does; False, saying why, when there's none left."""
        asked_for_pact = isinstance(level, PactSlot)
        level = int(level)
        level_left = char.get("spell_slots", {}).get(level, 0)
        pact_left = char.get("pact_slots", {}).get(level, 0)
        pact = asked_for_pact or (level_left <= 0 and pact_left > 0)
        if (pact_left if pact else level_left) <= 0:
            kind = "Pact Magic slots" if asked_for_pact else "slots"
            self._show_status(
                f"Nothing spent: {char['name']} has no level {level} {kind} left."
            )
            return False
        slots = char["pact_slots" if pact else "spell_slots"]
        slots[level] -= 1
        char.setdefault("stats", _default_stats())
        char["stats"]["spell_slots_used"] = char["stats"].get("spell_slots_used", 0) + 1
        level_key = spell_slots_used_key(level)
        char["stats"][level_key] = char["stats"].get(level_key, 0) + 1
        kind = "Pact Magic slot" if pact else "spell slot"
        self._log_event(
            f"{char['name']} uses a Level {level} {kind}",
            character=char["name"],
            action=Action.REMOVE_PACT_SLOT if pact else Action.REMOVE_SPELL_SLOT,
            value=level,
        )
        return True

    @undoable
    def _regain_spell_slot(self):
        """Give the source back a slot of the level picked: a Pact Magic slot
        while it has fewer of that level than when rested, else a spell slot."""
        char = self.selected_character
        if not char:
            self._show_status("Nothing regained: left-click a card to pick a source.")
            return
        level = self.spell_combo.currentIndex() + 1
        pact_left = char.get("pact_slots", {}).get(level, 0)
        pact = pact_left < max_pact_slots(char).get(level, 0)
        slots = char.setdefault("pact_slots" if pact else "spell_slots", {})
        slots[level] = slots.get(level, 0) + 1
        kind = "Pact Magic slot" if pact else "spell slot"
        self._log_event(
            f"{char['name']} regains a Level {level} {kind}",
            character=char["name"],
            action=Action.ADD_PACT_SLOT if pact else Action.ADD_SPELL_SLOT,
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
                value={"condition": entry["name"]},
            )
            self._end_spell_effects(entry)

    def _end_spell_effects(self, entry: dict):
        """Take what a concentration spell put on its targets off them, now
        that it's ended: entry["applied"] says what and on whom. Not what
        another running effect also holds, and not Unconscious from 0 HP."""
        entry["ends_with_conditions"] = False
        for applied in list(entry.get("applied", [])):
            if self._held_by_effect(applied, excluding=entry):
                continue
            condition = applied["condition"]
            for char in self.characters:
                if char["name"] != applied["target"]:
                    continue
                if condition not in char["conditions"]:
                    continue
                if condition != Condition.UNCONSCIOUS.value or char["hp"] > 0:
                    self._remove_condition_from(char, condition)
                break

    def _held_by_effect(self, applied: dict, excluding: dict | None = None) -> bool:
        """Whether a running spell, other than `excluding`, put this condition
        on this target."""
        return any(
            entry is not excluding and applied in entry.get("applied", [])
            for char in self.characters
            for entry in char.get("active_spells") or []
        )

    def _forget_effect_on(self, target: dict, condition: str):
        """Target has lost condition, so no spell holds it any more. A spell
        that lasted only as long as its conditions is over with the last."""
        applied = {"target": target["name"], "condition": condition}
        for char in self.characters:
            for entry in list(char.get("active_spells") or []):
                if applied not in entry.get("applied", []):
                    continue
                entry["applied"].remove(applied)
                if entry.get("ends_with_conditions") and not entry["applied"]:
                    char["active_spells"].remove(entry)
                    self._log_event(
                        f"{char['name']}'s {entry['name']} ends",
                        note_turn=False,
                        character=char["name"],
                        value={"condition": entry["name"]},
                    )
                    self._clear_concentration_if_unused(char)
                    self._rebuild_card(char)

    def _start_concentration(self, source: dict, name: str):
        """Source starts concentrating on `name`, which ends any concentration
        it had going. Concentration always belongs to the caster, regardless
        of who the spell targets."""
        remaining_spells = []
        for entry in source.get("active_spells") or []:
            if entry.get("concentration"):
                self._log_event(
                    f"{source['name']}'s {entry['name']} ends (concentration broken by casting {name})",
                    character=source["name"],
                    value={"condition": entry["name"]},
                )
                self._end_spell_effects(entry)
            else:
                remaining_spells.append(entry)
        source["active_spells"] = remaining_spells
        # A save still owed was for the spell that just ended.
        source.pop("concentration_checks", None)
        self._add_condition_to(source, CombatStatus.CONCENTRATING.value, source=source)

    def _tick_active_spells(self, started: list[dict], new_round: bool):
        """Deduct 6 seconds (one round) from the active spell timers due as the
        turn passes to `started` (`new_round` when that begins a round),
        expiring and logging any that reach zero, and dropping Concentrating if
        its spell expired. A timer counts on the turn the spell was cast, like
        a timed condition, so a late caster's spell lasts as long as anyone's;
        at the round's start if that combatant has no turn (any more), or for
        a timer that doesn't say."""
        started_names = {c["name"] for c in started}
        in_order = {c["name"] for c in self.initiative_order}
        ticked = False
        for char in self.characters:
            active_spells = char.get("active_spells")
            if not active_spells:
                continue
            remaining = []
            expired_concentration = False
            for entry in active_spells:
                ticks_on = entry.get("ticks_on")
                if ticks_on in in_order and ticks_on not in started_names:
                    remaining.append(entry)
                    continue
                if ticks_on not in started_names and not new_round:
                    remaining.append(entry)
                    continue
                ticked = True
                entry["time_left"] = max(entry["time_left"] - 6, 0)
                if entry["time_left"] > 0:
                    remaining.append(entry)
                else:
                    self._log_event(
                        f"{char['name']}'s {entry['name']} expires",
                        note_turn=False,
                        character=char["name"],
                        value={"condition": entry["name"]},
                    )
                    if entry.get("concentration"):
                        expired_concentration = True
                    self._end_spell_effects(entry)
            char["active_spells"] = remaining
            if expired_concentration:
                self._clear_concentration_if_unused(char)
        if ticked:
            self._rebuild_cards()

    @undoable
    def _remove_active_spell(self, char: dict, entry: dict):
        """Manually dismiss an active spell before its duration timer runs out."""
        active_spells = char.get("active_spells") or []
        if entry not in active_spells:
            return
        active_spells.remove(entry)
        self._log_event(
            f"{char['name']}'s {entry['name']} ends early",
            character=char["name"],
            value={"condition": entry["name"]},
        )
        self._end_spell_effects(entry)
        if entry.get("concentration"):
            self._clear_concentration_if_unused(char)
        self._rebuild_card(char)

    def _all_spells(self) -> list:
        """Every spell in the game, by level then name, read once (Cast Spell
        and the Custom Effect dialog's picker both list them)."""
        if not hasattr(self, "_spells_cache"):
            from CharacterContent.Spells.SpellFactory import SpellFactory

            self._spells_cache = sorted(
                SpellFactory.all_spells(), key=lambda s: (s.level, s.name)
            )
        return self._spells_cache

    def _spell_named(self, name: str):
        """The spell called `name` (as a Cast Spell badge is), or None."""
        if not hasattr(self, "_spells_by_name"):
            self._spells_by_name = {s.name: s for s in self._all_spells()}
        return self._spells_by_name.get(name)

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
        spells = self._all_spells()

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
                spell.level > 0 and has_slots(character) and len(choices) == 1
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

    def _count_spell_cast(
        self, caster: dict, name: str, level: int, slot_level: int | None
    ):
        """Count a cast of the spell `name` (of `level`, using a slot of
        slot_level, if any) in caster's stats, and log it so the party's
        replay counts it too. Cast Spell and the Custom Effect dialog share it."""
        stats = caster.setdefault("stats", _default_stats())
        stats["spells_cast"] = stats.get("spells_cast", 0) + 1
        increment_named_stat(stats, "spells_cast_by_name", name)
        upcast = f" at level {slot_level}" if (slot_level or 0) > level else ""
        self._log_event(
            f"{caster['name']} casts {name}{upcast}",
            character=caster["name"],
            action=Action.CAST_SPELL,
            value={"spell_name": name},
        )

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
        if not self._can_cast_or_say(source, spell.name):
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

        # Action economy: the caster spends the action, regardless of who it affects
        action_cost = casting_time_cost(spell)
        lacks = [
            spell_slot_lack(source, spell.level, slot_level),
            self._action_lack(source, action_cost),
        ]
        if not self._go_ahead_anyway(source, f"Cast {spell.name}", lacks):
            return

        self._count_spell_cast(source, spell.name, spell.level, slot_level)
        if slot_level is not None:
            self._cast_spell_slot_level(slot_level)

        if spell.is_concentration:
            self._start_concentration(source, spell.name)

        if action_cost is not None:
            self._add_action_use(action_cost, ask=False)

        tooltip_html = spell_badge_description(spell)
        badge_color = spell_badge_color(spell)

        # Duration -> a ticking bar, always tracked on the caster (source) regardless
        # of who the badge lands on — _tick_active_spells/_clear_concentration_if_unused
        # clear Concentrating off whichever character owns the expiring entry, and
        # Concentrating itself is only ever added to the caster.
        duration = spell.duration_seconds
        has_duration = bool(duration)

        # Store the tooltip description and badge color, and add the condition,
        # on every recipient (the caster for a self-cast, each target otherwise).
        applied = []
        if spell.is_concentration:
            for char in recipients:
                row = {"target": char["name"], "condition": spell.name}
                if spell.name not in char["conditions"] or self._held_by_effect(row):
                    applied.append(row)
        for char in list(recipients):
            char.setdefault("spell_condition_descriptions", {})[
                spell.name
            ] = tooltip_html
            char.setdefault("spell_condition_colors", {})[spell.name] = badge_color
            self._add_condition_to(char, spell.name, source=source)

        if has_duration:
            turn = self._current_turn_group()
            source.setdefault("active_spells", []).append(
                {
                    "name": spell.name,
                    "time_left": duration,
                    "duration": duration,
                    "concentration": spell.is_concentration,
                    "applied": applied,
                    "ticks_on": turn[0]["name"] if turn else None,
                }
            )

        self._save_fight_state()
        self._refresh_selected_card()


def spell_badge_description(spell) -> str:
    """What a condition badge a spell put on a creature shows when clicked or
    hovered: the spell's card (level, school, casting time, range, target,
    components, duration) and its rules text, as HTML."""
    tags = []
    if spell.is_concentration:
        tags.append("Concentration")
    if spell.is_ritual:
        tags.append("Ritual")
    tag_text = f" [{', '.join(tags)}]" if tags else ""
    level = "Cantrips" if spell.level == 0 else f"Level {spell.level}"
    target_text = (
        spell.target.value.replace("_", " ").title()
        if spell.target is not None
        else "None"
    )
    return (
        f"<b style='color:#c9a84c; font-size:14px;'>{spell.name}</b>{tag_text}"
        f"<br><span style='color:#a0a0b0;'>{level} · {spell.school}</span>"
        f"<br><br><b>Casting Time:</b> {spell.casting_time}"
        f"<br><b>Range:</b> {spell.range}"
        f"<br><b>Target:</b> {target_text}"
        f"<br><b>Components:</b> {spell.components}"
        f"<br><b>Duration:</b> {spell.duration}"
        f"<br><br>{spell.description.replace(chr(10) + chr(10), '<br><br>')}"
    )


def spell_badge_color(spell) -> str:
    """A spell's condition badge's color: its school's."""
    from CharacterContent.Spells.SpellFactory import Spell

    return Spell.get_school_color(spell.school)
