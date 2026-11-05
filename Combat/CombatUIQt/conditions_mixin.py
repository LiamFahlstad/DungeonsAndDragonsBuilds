"""Conditions mixin for CombatAppQt."""

import re
from html import escape

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import Action, CombatStatus
from Combat.WildShape import current_form, form_badge
from Core.Definitions import DamageType
from Core.Rules import SECONDS_PER_ROUND
from .amounts import AmountError, parse_amount
from .attack_rolls import AttackRoll, parse_attack_roll
from .effect_options import (
    COLLAPSED_CATEGORIES,
    effect_options,
    spell_slot_choices,
)
from .monster_actions import legendary_resistances_left
from .player_view import note_condition_immunity
from .saves import (
    ABILITIES,
    ATTACK_ROLL,
    FEATURE,
    ROLL_MODES,
    SAVING_THROW,
    SPELL,
    CustomEffect,
    EffectOption,
    is_immune_to,
    known_attack_bonus,
    known_save_dc,
    read_damage,
    roll_attack,
    roll_save,
    rolled_damage,
)
from .stats import _default_stats, increment_named_stat
from .state import CombatWindowState
from .styles import QSS
from .tree_filter import filter_category_tree, first_visible_item
from .undo import undoable

# Conditions that incapacitate a creature and break concentration per 2024 D&D rules
INCAPACITATING_CONDITIONS = {
    "Incapacitated",
    "Paralyzed",
    "Petrified",
    "Stunned",
    "Unconscious",
}

# The durations the Custom Condition dialog offers, as (label, duration). A
# duration is None (until removed), {"seconds": n} (counted down a round at a
# time, on the turn it was given in), or {"until": "start" | "end", "of":
# "source" | "target"} (ends at the start or end of the source's, or each
# target's, next turn). "{source}" in a label is the source's name.
CUSTOM_CONDITION_DURATIONS: list[tuple[str, dict | None]] = [
    ("Until removed", None),
    ("Until the start of {source}'s next turn", {"until": "start", "of": "source"}),
    ("Until the end of {source}'s next turn", {"until": "end", "of": "source"}),
    ("Until the start of the target's next turn", {"until": "start", "of": "target"}),
    ("Until the end of the target's next turn", {"until": "end", "of": "target"}),
    ("1 round (6 seconds)", {"seconds": SECONDS_PER_ROUND}),
    ("1 minute (10 rounds)", {"seconds": 60}),
    ("10 minutes", {"seconds": 10 * 60}),
    ("1 hour", {"seconds": 60 * 60}),
]

_CUSTOM_DIALOG_WIDTH = 900  # the main window's minimum
_PICKER_WIDTH = 240
# The typed-roll rows scroll past about four targets.
_TYPED_ROWS_MAX_HEIGHT = 140
_NATURAL_ROLL = re.compile(r"nat(?:ural)?\s*\d+", re.IGNORECASE)
_WHOLE_NUMBER = re.compile(r"-?\d+")
MAX_SAVE_DC = 40
MIN_ATTACK_BONUS = -10
MAX_ATTACK_BONUS = 30
# How long a concentration effect runs with no time on it: the longest there is
# in general use, for the GM to end by hand or by losing concentration.
LONGEST_CONCENTRATION = 60 * 60
# Dice, stood in for by a number when only the type in the text matters.
_DICELESS = re.compile(r"\d+d\d+")

# The units a custom duration can be typed in, as seconds per unit.
CUSTOM_DURATION_UNITS = {"rounds": SECONDS_PER_ROUND, "minutes": 60, "seconds": 1}
MAX_DURATION_AMOUNT = 9999


def custom_duration(seconds: int) -> tuple[int, str] | None:
    """`seconds` as the Custom... duration's amount and unit, the biggest unit
    that fits it exactly. None if it's longer than that can say (days)."""
    for unit, per_unit in sorted(CUSTOM_DURATION_UNITS.items(), key=lambda u: -u[1]):
        if seconds % per_unit == 0 and seconds // per_unit <= MAX_DURATION_AMOUNT:
            return seconds // per_unit, unit
    return None


def _option_tooltip(option: EffectOption) -> str:
    """A picker row's tooltip: what the row says, then its rules text. Rich
    text, so Qt wraps it."""
    text = escape(option.tooltip, quote=False).replace("\n", "<br>")
    return f"<b>{escape(option.row_text, quote=False)}</b><br>{text}"


class ConditionsMixin(CombatWindowState):
    """Mixin for condition and visibility management."""

    @undoable
    def _add_condition_to(self, char: dict, cond: str, source: dict | None = None):
        if cond not in char["conditions"]:
            char["conditions"].append(cond)
            char.setdefault("stats", _default_stats())
            char["stats"]["conditions_received"] = (
                char["stats"].get("conditions_received", 0) + 1
            )
            increment_named_stat(char["stats"], "conditions_received_by_name", cond)
            source_name = source["name"] if source is not None else None
            if source is not None:
                source.setdefault("stats", _default_stats())
                source["stats"]["conditions_given"] = (
                    source["stats"].get("conditions_given", 0) + 1
                )
                increment_named_stat(source["stats"], "conditions_given_by_name", cond)
            cond_value = {
                "condition": cond,
                "source_name": source_name,
                "target_name": char["name"],
            }
            source_suffix = (
                f" from {source_name}"
                if source_name and source_name != char["name"]
                else ""
            )
            self._log_event(
                f"{char['name']} gains {cond}{source_suffix}",
                character=char["name"],
                action=Action.ADD_CONDITION,
                value=cond_value,
            )
            self._rebuild_card(char)
            # Break concentration if an incapacitating condition is applied to a concentrating character
            if (
                cond in INCAPACITATING_CONDITIONS
                and cond != "Concentrating"
                and "Concentrating" in char.get("conditions", [])
            ):
                self._remove_condition_from(char, "Concentrating", source=char)
            # So does a Wild Shape form (which a knock-out's Unconscious ends too).
            if cond in INCAPACITATING_CONDITIONS and current_form(char):
                self._leave_wild_shape(char, reason=cond)

    @undoable
    def _remove_condition_from(self, char: dict, cond: str, source: dict | None = None):
        if cond in char["conditions"]:
            char["conditions"].remove(cond)
            char.get("spell_condition_descriptions", {}).pop(cond, None)
            char.get("spell_condition_colors", {}).pop(cond, None)
            char.get("feature_condition_descriptions", {}).pop(cond, None)
            char.get("feature_condition_colors", {}).pop(cond, None)
            char.get("custom_condition_descriptions", {}).pop(cond, None)
            if "timed_conditions" in char:
                char["timed_conditions"] = [
                    e for e in char["timed_conditions"] if e["name"] != cond
                ]
            source_name = source["name"] if source is not None else None
            cond_value = {
                "condition": cond,
                "source_name": source_name,
                "target_name": char["name"],
            }
            source_suffix = (
                f" from {source_name}"
                if source_name and source_name != char["name"]
                else ""
            )
            self._log_event(
                f"{char['name']} loses {cond}{source_suffix}",
                character=char["name"],
                action=Action.REMOVE_CONDITION,
                value=cond_value,
            )
            self._forget_effect_on(char, cond)
            self._drop_repeat_save(char, cond)
            if cond == CombatStatus.CONCENTRATING.value:
                char.pop("concentration_checks", None)
                self._end_concentration_spells(char)
            # Taking the Wild Shape badge off is leaving the form early.
            form = current_form(char)
            if form is not None and cond == form_badge(form):
                self._leave_wild_shape(char)
            self._rebuild_card(char)

    @undoable
    def _add_condition(self):
        """Add the selected condition to every target, attributed to the source
        (mirrors Damage/Heal/Temp HP's source → target model)."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return
        source = self.selected_character or self._current_turn_character()
        cond = self.condition_combo.currentText()
        for target in list(self.target_characters):
            self._add_condition_to(target, cond, source=source)

    @undoable
    def _remove_condition(self):
        if not self.target_characters:
            self._show_status("Nothing removed: right-click a card to pick a target.")
            return
        source = self.selected_character or self._current_turn_character()
        cond = self.condition_combo.currentText()
        if not any(cond in t["conditions"] for t in self.target_characters):
            self._show_status(f"Nothing removed: no target has {cond}.")
            return
        for target in list(self.target_characters):
            self._remove_condition_from(target, cond, source=source)

    @undoable
    def _add_custom_condition(
        self,
        cond: str,
        duration: dict | None = None,
        notes: str = "",
        targets: list[dict] | None = None,
    ):
        """Give every target (or those of `targets`) `cond`, any text (a rules
        condition or an effect like "Hexed" or "-2 AC"), attributed to the
        source, for `duration` (see CUSTOM_CONDITION_DURATIONS) and with
        `notes` as its tooltip. Giving it again replaces its duration."""
        cond = cond.strip()
        targets = self.target_characters if targets is None else targets
        if not cond or not targets:
            return
        source = self.selected_character or self._current_turn_character()
        turn = self._current_turn_group()
        for target in list(targets):
            if notes.strip():
                target.setdefault("custom_condition_descriptions", {})[
                    cond
                ] = notes.strip()
            self._add_condition_to(target, cond, source=source)
            timers = [
                e for e in target.get("timed_conditions", []) if e["name"] != cond
            ]
            entry = _timed_condition_entry(cond, duration, source, target, turn)
            if entry is not None:
                timers.append(entry)
            target["timed_conditions"] = timers
            self._rebuild_card(target)
        self._save_fight_state()

    def _tick_timed_conditions(
        self, ended: list[dict], started: list[dict], new_round: bool
    ):
        """Count timed conditions down as the turn passes from `ended` to
        `started` (`new_round` when that begins a round), ending each one
        whose time or turns run out."""
        ended_names = {c["name"] for c in ended}
        started_names = {c["name"] for c in started}
        in_order = {c["name"] for c in self.initiative_order}
        for char in self.characters:
            entries = char.get("timed_conditions")
            if not entries:
                continue
            for entry in list(entries):
                if "time_left" in entry:
                    # A round passes on the turn it was given in, or at the
                    # round's start if that combatant has no turn (any more).
                    ticks_on = entry.get("ticks_on")
                    if ticks_on in started_names or (
                        new_round and ticks_on not in in_order
                    ):
                        entry["time_left"] = max(
                            entry["time_left"] - SECONDS_PER_ROUND, 0
                        )
                    expired = entry["time_left"] == 0
                else:
                    boundary = ended_names if entry["until"] == "end" else started_names
                    if entry["of"] in boundary:
                        entry["turns_left"] -= 1
                    expired = entry["turns_left"] <= 0
                if expired:
                    self._log_event(
                        f"{char['name']}'s {entry['name']} expires",
                        note_turn=False,
                        character=char["name"],
                    )
                    self._remove_condition_from(char, entry["name"])
            self._rebuild_card(char)

    def _custom_condition_suggestions(self) -> list[str]:
        """What the Custom Condition dialog's name box offers: the rules
        conditions, then everything else a combatant has right now."""
        others = {
            cond
            for char in self.characters
            for cond in char.get("conditions", [])
            if cond not in self.conditions
        }
        return list(self.conditions) + sorted(others)

    @undoable
    def _apply_custom_effect(self, effect: CustomEffect):
        """Apply a Custom dialog effect to every living target: what it costs
        the source, then with an attack roll, the source rolls against each
        one's AC: a hit takes it all, a critical hit with the dice rolled twice
        over, and a miss takes nothing. With a saving throw, each one rolls, and
        a save halves the damage (or avoids it) and avoids the condition. With
        neither, everyone takes it all, except those marked ½ Saved, who saved
        by hand and count the same."""
        living = [
            t for t in self.target_characters if self._char_death_state(t) != "dead"
        ]
        if not living:
            self._show_status("Nothing applied: every target is dead.")
            return
        source = self.selected_character or self._current_turn_character()
        caster = self.selected_character
        label = effect.name or effect.condition or "the effect"
        logged_use = False
        if caster is not None:
            if effect.pick is not None:
                used = self._use_pick(caster, effect)
                if used is None:
                    return
                logged_use = used
            if effect.slot_level is not None:
                self._cast_spell_slot_level(effect.slot_level)
            if effect.action_cost is not None:
                self._add_action_use(effect.action_cost)
            if effect.concentration:
                self._start_concentration(caster, label)
        if (
            effect.attack_bonus is not None
            and effect.name
            and source is not None
            and not logged_use
        ):
            # The attack lines stay as the player link reads them (public_log.py).
            self._log_event(
                f"{source['name']} uses {effect.name}", character=source["name"]
            )

        results = []
        attacks = []
        applied = []
        for target in living:
            saved = any(target is s for s in self._saved_targets)
            damage = effect.damage
            if effect.attack_bonus is not None:
                roll = effect.typed_attacks.get(id(target)) or roll_attack(
                    effect.attack_bonus, effect.mode
                )
                hit, attack = self._resolve_attack_roll(target, roll, source)
                results.append(hit is not False)
                attacks.append(attack)
                if hit is False:
                    continue
                saved = False
                if roll.is_critical:
                    damage = effect.critical_damage or damage
            if effect.ability is not None:
                saved = self._roll_effect_save(target, effect)
                results.append(saved)
            avoided = effect.ability is not None and saved and not effect.half_on_save
            if damage and not avoided:
                self._deal_damage(
                    target, damage, source, effect.count_resistances, saved
                )
                if not any(c is target for c in self.characters):
                    continue  # a summon that vanished at 0 HP
            if not effect.condition or saved:
                continue
            row = {"target": target["name"], "condition": effect.condition}
            already_had = effect.condition in target["conditions"]
            held_by_a_spell = self._held_by_effect(row)
            if self._give_effect_condition(target, effect):
                if held_by_a_spell or not already_had:
                    applied.append(row)

        if effect.concentration and caster is not None:
            self._hold_concentration(caster, label, effect, applied)
        if effect.damage and source is not None:
            source["_last_damage_type"] = effect.damage[-1][1]
        self._saved_targets = []
        self._update_target_label()
        for target in self.target_characters:
            self._rebuild_card(target)
        self._save_fight_state()
        self._show_effect_summary(effect, results)
        if logged_use and effect.pick is not None and effect.pick.monster_action:
            self._refresh_views()  # the turn column's button shows it spent
        if attacks:  # last, as logging clears the status line
            self._show_status("; ".join(attacks))

    def _use_pick(self, caster: dict, effect: CustomEffect) -> bool | None:
        """Count what the dialog's pick was as used by caster, as Cast Spell,
        Enable Feature and the turn column's buttons do. Returns whether that
        logged its use, or None, having said why, if it can't be used now."""
        option = effect.pick
        assert option is not None  # the caller checks
        if option.kind == SPELL:
            if not self._can_cast_or_say(caster, option.name):
                return None
            self._count_spell_cast(
                caster, option.name, option.spell_level, effect.slot_level
            )
            return True
        if option.kind == FEATURE:
            self._count_feature_use(caster, option.name, option.counts_uses)
            return True
        if option.monster_action is not None:
            return self._spend_monster_action(caster, option.monster_action)
        return False

    def _effect_picker(
        self, source: dict | None
    ) -> tuple[QLineEdit, QTreeWidget, dict[str, QTreeWidgetItem]]:
        """The Custom Effect dialog's search box and list of what the source
        can use (effect_options), by category. What can't be used now is
        greyed out."""
        search_box = QLineEdit()
        search_box.setObjectName("effectSearch")
        search_box.setPlaceholderText("Search attacks, spells, features…")
        search_box.setFixedWidth(_PICKER_WIDTH)
        tree = QTreeWidget()
        tree.setObjectName("effectOptions")
        tree.setHeaderHidden(True)
        tree.setFixedWidth(_PICKER_WIDTH)
        category_items: dict[str, QTreeWidgetItem] = {}
        for title, options in effect_options(source, self._all_spells()):
            category = QTreeWidgetItem([title])
            category.setFirstColumnSpanned(True)
            tree.addTopLevelItem(category)
            category_items[title] = category
            for option in options:
                item = QTreeWidgetItem([option.row_text])
                item.setData(0, Qt.ItemDataRole.UserRole, option)
                item.setToolTip(0, _option_tooltip(option))
                category.addChild(item)
                item.setDisabled(option.is_unavailable)
            category.setExpanded(title not in COLLAPSED_CATEGORIES)

        def apply_filter(query: str):
            filter_category_tree(
                category_items,
                query.strip().lower(),
                lambda option, typed: typed in option.name.lower(),
            )

        search_box.textChanged.connect(apply_filter)
        return search_box, tree, category_items

    def _hold_concentration(
        self, caster: dict, label: str, effect: CustomEffect, applied: list[dict]
    ):
        """Caster's concentration on the effect, tied to what it put on whom.
        If the effect itself just ended that concentration (the caster was
        among its targets), it's over already."""
        duration = effect.duration or {}
        seconds = duration.get("seconds", LONGEST_CONCENTRATION)
        turn = self._current_turn_group()
        entry = {
            "name": label,
            "time_left": seconds,
            "duration": seconds,
            "concentration": True,
            "applied": applied,
            "ticks_on": turn[0]["name"] if turn else None,
            # With a turn for a duration, the conditions are what end first.
            "ends_with_conditions": "until" in duration and bool(applied),
        }
        if CombatStatus.CONCENTRATING.value not in caster["conditions"]:
            self._end_spell_effects(entry)
            return
        caster.setdefault("active_spells", []).append(entry)
        self._rebuild_card(caster)

    def _give_effect_condition(self, target: dict, effect: CustomEffect) -> bool:
        """Give target the effect's condition, unless it's died of the effect
        or is immune. Returns whether it has it from this effect now."""
        if self._char_death_state(target) == "dead":
            return False
        if is_immune_to(target, effect.condition):
            readable = self._log_event(
                f"{target['name']} is immune to {effect.condition}",
                character=target["name"],
            )
            if readable:
                note_condition_immunity(target, effect.condition)
            return False
        self._add_custom_condition(
            effect.condition, effect.duration, effect.notes, [target]
        )
        if effect.repeat_save and effect.ability is not None:
            self._drop_repeat_save(target, effect.condition)
            target.setdefault("repeat_saves", []).append(
                {
                    "condition": effect.condition,
                    "ability": effect.ability,
                    "dc": effect.dc,
                    "mode": effect.mode,
                    "use_legendary_resistance": effect.use_legendary_resistance,
                }
            )
        return True

    def _drop_repeat_save(self, char: dict, condition: str):
        """Char has no more repeat save to end condition."""
        entries = [
            e for e in char.get("repeat_saves", []) if e["condition"] != condition
        ]
        if entries:
            char["repeat_saves"] = entries
        else:
            char.pop("repeat_saves", None)

    def _roll_effect_save(self, target: dict, effect: CustomEffect) -> bool:
        """Target's save against the effect, logged. Legendary Resistance turns
        a failure into a success, if the dialog said to use it."""
        assert effect.ability is not None  # the caller checks
        name = target["name"]
        result = roll_save(
            target,
            effect.ability,
            effect.dc,
            effect.mode,
            effect.typed_totals.get(id(target)),
        )
        ability = next(full for full, short in ABILITIES if short == effect.ability)
        against = f" against {effect.name}" if effect.name else ""
        rolled = "" if result.total is None else f", rolled {result.total}"
        note = f", {result.note}" if result.note else ""
        verb = "makes" if result.success else "fails"
        self._log_event(
            f"{name} {verb} a DC {effect.dc} {ability} save{against}{rolled}{note}",
            character=name,
            value={"condition": effect.condition},
        )
        if result.success:
            return True
        if effect.use_legendary_resistance and legendary_resistances_left(target) > 0:
            self._use_legendary_resistance(target)
            return True
        return False

    def _repeat_saves(self, char: dict):
        """As char's turn ends, the saves that could end a condition on it. A
        monster rolls, keeping the roll if the turn is undone and passed again;
        a player rolls at the table, so they get a reminder."""
        if self._char_death_state(char) == "dead":
            return
        for entry in list(char.get("repeat_saves", [])):
            condition = entry["condition"]
            if condition not in char["conditions"]:
                self._drop_repeat_save(char, condition)
                continue
            ability = next(f for f, short in ABILITIES if short == entry["ability"])
            if char.get("_is_player"):
                self._turn_start_notes.append(
                    f"{char['name']}: DC {entry['dc']} {ability} save to end {condition}"
                )
                continue
            self._roll_repeat_save(char, entry, ability)

    def _roll_repeat_save(self, char: dict, entry: dict, ability: str):
        """A monster's save to end a condition, and what comes of it."""
        condition = entry["condition"]
        rolls = char.setdefault("_repeat_rolls", {})
        turn = (self.round_number, self.current_turn_idx, condition, entry["ability"])
        result = roll_save(
            char, entry["ability"], entry["dc"], entry["mode"], rolls.get(turn)
        )
        rolls[turn] = result.total
        rolled = "" if result.total is None else f" (rolled {result.total})"
        note = f" ({result.note})" if result.note else ""
        saved = result.success
        if not saved and entry["use_legendary_resistance"]:
            if legendary_resistances_left(char) > 0:
                self._use_legendary_resistance(char)
                saved = True
        name = char["name"]
        if saved:
            self._log_event(
                f"{name} ends {condition} with a DC {entry['dc']} {ability}"
                f" save{rolled}{note}",
                character=name,
            )
            self._remove_condition_from(char, condition)
            self._turn_start_notes.append(f"{name} saved{rolled}: {condition} ends")
        else:
            self._log_event(
                f"{name} fails a DC {entry['dc']} {ability} save and keeps"
                f" {condition}{rolled}{note}",
                character=name,
            )
            self._turn_start_notes.append(f"{name} failed{rolled}: still {condition}")

    def _show_effect_summary(self, effect: CustomEffect, results: list[bool]):
        """Say how it went in the turn column; the log has each target's roll."""
        words = [effect.name] if effect.name else []
        if effect.attack_bonus is not None:
            hits = sum(results)
            words.append(f"Attack: {hits} hit, {len(results) - hits} missed")
        if effect.ability is not None:
            saved = sum(results)
            words.append(
                f"DC {effect.dc} {effect.ability}: {saved} saved,"
                f" {len(results) - saved} failed"
            )
        words += [f"{amount} {damage_type}" for amount, damage_type in effect.damage]
        if effect.condition:
            words.append(effect.condition)
        self._action_result_label.setText(" · ".join(words))
        self._action_result_label.setToolTip("")

    def _show_custom_condition_dialog(self):
        """Set up an effect on every target (see _apply_custom_effect): what
        it costs the source, a saving throw or an attack roll, damage, and a
        condition with its duration and a note."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return
        source = self.selected_character or self._current_turn_character()
        caster = self.selected_character

        dlg = QDialog(self._window)
        dlg.setWindowTitle("Custom Effect")
        dlg.setStyleSheet(QSS)
        dlg.setFixedWidth(_CUSTOM_DIALOG_WIDTH)
        outer = QHBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(14)
        # What the source can use, on the left: a pick fills in the form.
        search_box, tree, category_items = self._effect_picker(source)
        picker = QVBoxLayout()
        picker.setSpacing(6)
        picker.addWidget(search_box)
        picker.addWidget(tree, stretch=1)
        outer.addLayout(picker)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        outer.addLayout(layout, stretch=1)

        who = f"Targets: {', '.join(c['name'] for c in self.target_characters)}"
        if source is not None:
            who += f"\nSource: {source['name']}"
        who_lbl = QLabel(who)
        who_lbl.setObjectName("secondary")
        who_lbl.setWordWrap(True)
        layout.addWidget(who_lbl)

        name_input = QLineEdit()
        name_input.setObjectName("effectName")
        name_input.setPlaceholderText("Name for the log (optional), e.g. Fireball")
        layout.addWidget(name_input)

        # What to check about a pick, and what a monster's action does besides.
        note_lbl = QLabel("")
        note_lbl.setObjectName("effectNote")
        note_lbl.setWordWrap(True)
        note_lbl.hide()
        layout.addWidget(note_lbl)

        columns = QHBoxLayout()
        columns.setSpacing(20)
        save_col = QVBoxLayout()
        save_col.setSpacing(6)
        effect_col = QVBoxLayout()
        effect_col.setSpacing(6)
        columns.addLayout(save_col, stretch=1)
        columns.addLayout(effect_col, stretch=1)
        layout.addLayout(columns)

        # The saving throw or attack roll, and what it decides
        save_col.addWidget(self._section_header("Roll"))
        roll_row = QHBoxLayout()
        roll_combo = QComboBox()
        roll_combo.setObjectName("rollKind")
        roll_combo.addItems((SAVING_THROW, ATTACK_ROLL))
        roll_combo.setCurrentText(self._custom_save["roll"])
        roll_row.addWidget(roll_combo, stretch=1)
        ability_combo = QComboBox()
        ability_combo.setObjectName("saveAbility")
        ability_combo.addItem("No saving throw", None)
        for full, short in ABILITIES:
            ability_combo.addItem(full, short)
        ability_combo.setCurrentIndex(
            max(ability_combo.findData(self._custom_save["ability"]), 0)
        )
        roll_row.addWidget(ability_combo, stretch=1)
        save_col.addLayout(roll_row)

        dc_row = QHBoxLayout()
        dc_label = QLabel("DC:")
        dc_row.addWidget(dc_label)
        dc_input = QSpinBox()
        dc_input.setObjectName("saveDc")
        dc_input.setRange(1, MAX_SAVE_DC)
        same_source = self._custom_save["source"] is source
        known_dc = None if same_source else known_save_dc(source)
        dc_input.setValue(known_dc or self._custom_save["dc"])
        dc_row.addWidget(dc_input)
        bonus_label = QLabel("Bonus:")
        dc_row.addWidget(bonus_label)
        bonus_input = QSpinBox()
        bonus_input.setObjectName("attackBonus")
        bonus_input.setRange(MIN_ATTACK_BONUS, MAX_ATTACK_BONUS)
        bonus_input.setToolTip("What the source adds to its d20")
        known_bonus = None if same_source else known_attack_bonus(source)
        bonus_input.setValue(
            self._custom_save["bonus"] if known_bonus is None else known_bonus
        )
        dc_row.addWidget(bonus_input)
        mode_combo = QComboBox()
        mode_combo.setObjectName("saveMode")
        mode_combo.addItems(ROLL_MODES)
        dc_row.addWidget(mode_combo, stretch=1)
        save_col.addLayout(dc_row)

        half_box = QCheckBox("Half damage on a save")
        half_box.setObjectName("halfOnSave")
        half_box.setChecked(self._custom_save["half"])
        save_col.addWidget(half_box)

        repeat_box = QCheckBox("Repeat the save at the end of each turn")
        repeat_box.setObjectName("repeatSave")
        repeat_box.setToolTip(
            "A save ends the condition. Monsters roll by themselves; players"
            " get a reminder."
        )
        save_col.addWidget(repeat_box)

        resist_box = QCheckBox("Use Legendary Resistance on a failed save")
        resist_box.setObjectName("useLegendaryResistance")
        can_resist = any(
            legendary_resistances_left(t) > 0 for t in self.target_characters
        )
        save_col.addWidget(resist_box)

        def typed_rows(
            chars: list[dict], object_name: str, hint: str
        ) -> tuple[QWidget, dict[int, QLineEdit]]:
            """A box for each of chars, for what was rolled at the table. Many
            targets scroll, so the dialog still fits the smallest window."""
            rows = QWidget()
            rows_layout = QVBoxLayout(rows)
            rows_layout.setContentsMargins(0, 0, 0, 0)
            rows_layout.setSpacing(6)
            inputs = {}
            for char in chars:
                row = QHBoxLayout()
                row.addWidget(QLabel(char["name"]), stretch=1)
                total_input = QLineEdit()
                total_input.setObjectName(object_name)
                total_input.setPlaceholderText(hint)
                total_input.setAccessibleName(char["name"])
                row.addWidget(total_input, stretch=1)
                rows_layout.addLayout(row)
                inputs[id(char)] = total_input
            scroll = QScrollArea()
            scroll.setWidget(rows)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setFixedHeight(min(rows.sizeHint().height(), _TYPED_ROWS_MAX_HEIGHT))
            save_col.addWidget(scroll)
            return scroll, inputs

        # A roll made at the table is typed in; the rest are rolled. Each target
        # rolls a save for itself, and the source an attack against each one.
        save_rows, typed_inputs = typed_rows(
            self.target_characters, "typedTotal", "Total, or blank to roll"
        )
        for total_input in typed_inputs.values():
            total_input.setToolTip(
                "The total with the save bonus already in it, like 14 or 9+5."
                " Blank rolls for them."
            )
        attack_rows, attack_inputs = typed_rows(
            self.target_characters, "typedAttack", "Total, or blank to roll"
        )
        for roll_input in attack_inputs.values():
            roll_input.setToolTip(
                "The total with the bonus already in it, like 17 or 12+5, or"
                " nat 20 or nat 1. Blank rolls for the source."
            )

        # What it costs the source
        save_col.addWidget(self._section_header("Source"))
        cost_row = QHBoxLayout()
        slot_combo = QComboBox()
        slot_combo.setObjectName("spellSlot")
        slot_combo.addItem("No spell slot", None)
        for label, level in spell_slot_choices(caster or {}, 1):
            if level is not None:
                slot_combo.addItem(label, level)
        cost_row.addWidget(slot_combo, stretch=1)
        action_combo = QComboBox()
        action_combo.setObjectName("actionCost")
        action_combo.addItem("No action", None)
        for action_type in self.ACTION_ECONOMY_TYPES:
            action_combo.addItem(action_type, action_type)
        cost_row.addWidget(action_combo, stretch=1)
        save_col.addLayout(cost_row)
        concentrate_box = QCheckBox("Source concentrates on it")
        concentrate_box.setObjectName("sourceConcentrates")
        concentrate_box.setToolTip(
            "Starts Concentrating, ending any other concentration. When it"
            " ends, the condition comes off the targets."
        )
        save_col.addWidget(concentrate_box)
        for widget in (slot_combo, action_combo, concentrate_box):
            widget.setEnabled(caster is not None)
        save_col.addStretch()

        # The effect
        effect_col.addWidget(self._section_header("Damage"))
        damage_row = QHBoxLayout()
        damage_input = QLineEdit()
        damage_input.setObjectName("effectDamage")
        damage_input.setPlaceholderText("e.g. 8d6, 28, 2d6 sl + 1d4 fi")
        damage_input.setToolTip("Dice are rolled once, for everyone it hits")
        damage_row.addWidget(damage_input, stretch=3)
        type_combo = QComboBox()
        type_combo.setObjectName("damageType")
        type_combo.addItem("— Type —", None)
        for damage_type in DamageType:
            type_combo.addItem(damage_type.value, damage_type.value)
        if source is not None and self.settings.remember_damage_type:
            type_combo.setCurrentIndex(
                max(type_combo.findData(source.get("_last_damage_type")), 0)
            )
        damage_row.addWidget(type_combo, stretch=2)
        effect_col.addLayout(damage_row)

        resistances_box = QCheckBox("Count resistances and immunities")
        resistances_box.setObjectName("countResistances")
        resistances_box.setChecked(True)
        effect_col.addWidget(resistances_box)

        condition_header = self._section_header("")
        effect_col.addWidget(condition_header)
        name_combo = QComboBox()
        name_combo.setObjectName("conditionName")
        name_combo.setEditable(True)
        name_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        suggestions = self._custom_condition_suggestions()
        name_combo.addItems(suggestions)
        name_combo.setCurrentText("")
        name_edit = name_combo.lineEdit()
        assert name_edit is not None  # an editable combo box has one
        name_edit.setPlaceholderText("e.g. Hexed, Restrained by vines, -2 AC...")
        effect_col.addWidget(name_combo)

        notes_input = QLineEdit()
        notes_input.setObjectName("conditionNotes")
        notes_input.setPlaceholderText("Notes (optional, shown on hover)")
        effect_col.addWidget(notes_input)

        effect_col.addWidget(QLabel("Duration:"))
        duration_combo = QComboBox()
        duration_combo.setObjectName("conditionDuration")
        for label, duration in CUSTOM_CONDITION_DURATIONS:
            if duration is not None and duration.get("of") == "source":
                if source is None:
                    continue
                label = label.format(source=source["name"])
            duration_combo.addItem(label, duration)
        duration_combo.addItem("Custom...", "custom")
        effect_col.addWidget(duration_combo)

        custom_row = QHBoxLayout()
        amount_input = QSpinBox()
        amount_input.setObjectName("durationAmount")
        amount_input.setRange(1, 9999)
        custom_row.addWidget(amount_input)
        unit_combo = QComboBox()
        unit_combo.setObjectName("durationUnit")
        unit_combo.addItems(list(CUSTOM_DURATION_UNITS))
        custom_row.addWidget(unit_combo)
        custom_widgets = (amount_input, unit_combo)
        effect_col.addLayout(custom_row)
        effect_col.addStretch()

        def show_custom_row():
            for widget in custom_widgets:
                widget.setVisible(duration_combo.currentData() == "custom")

        def show_roll_controls():
            is_attack = roll_combo.currentText() == ATTACK_ROLL
            has_save = not is_attack and ability_combo.currentData() is not None
            for widget in (ability_combo, dc_label, dc_input, half_box, repeat_box):
                widget.setVisible(not is_attack)
            for widget in (bonus_label, bonus_input):
                widget.setVisible(is_attack)
            resist_box.setVisible(can_resist and not is_attack)
            save_rows.setVisible(bool(typed_inputs) and not is_attack)
            attack_rows.setVisible(bool(attack_inputs) and is_attack)
            mode_combo.setEnabled(has_save or is_attack)
            for widget in (dc_input, half_box, repeat_box, resist_box):
                widget.setEnabled(has_save)
            for total_input in typed_inputs.values():
                total_input.setEnabled(has_save)
            condition_header.setText(
                "Condition (on a hit)" if is_attack else "Condition (on a failed save)"
            )

        def show_typed_type(text: str):
            try:
                parts = rolled_damage(_DICELESS.sub("1", text))
            except AmountError:
                return
            if parts[0][1] is not None:
                type_combo.setCurrentIndex(type_combo.findData(parts[0][1]))

        duration_combo.currentIndexChanged.connect(show_custom_row)
        roll_combo.currentIndexChanged.connect(show_roll_controls)
        ability_combo.currentIndexChanged.connect(show_roll_controls)
        damage_input.textChanged.connect(show_typed_type)
        show_custom_row()
        show_roll_controls()

        problem_lbl = QLabel("")
        problem_lbl.setObjectName("statusLabel")
        problem_lbl.setWordWrap(True)
        layout.addWidget(problem_lbl)

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.setAutoDefault(False)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setAutoDefault(False)
        btn_row.addWidget(apply_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        # Enter in a text box and the Apply button can both fire; apply once.
        applied: list[bool] = []

        def typed_totals() -> dict[int, int] | None:
            """The totals typed, or None having said what's wrong with one: a
            total ("14") or a sum ("9+5"), as an attack's. A total can be
            negative: a low roll with a negative save. A natural 20 or 1 is
            nothing special on a save, so it's the total that's wanted."""
            totals = {}
            for key, total_input in typed_inputs.items():
                text = total_input.text().strip()
                if not text:
                    continue
                if _NATURAL_ROLL.fullmatch(text):
                    problem_lbl.setText(
                        f"'{text}': a natural roll is nothing special on a"
                        " save. Type the total instead."
                    )
                    return None
                total = int(text) if _WHOLE_NUMBER.fullmatch(text) else None
                if total is None:
                    total = parse_amount(text)
                if total is None:
                    problem_lbl.setText(f"'{text}' isn't a saving throw total.")
                    return None
                totals[key] = total
            return totals

        def typed_attacks() -> dict[int, AttackRoll] | None:
            """The attack rolls typed, or None having said what's wrong with one."""
            rolls = {}
            for key, roll_input in attack_inputs.items():
                text = roll_input.text().strip()
                if not text:
                    continue
                roll = parse_attack_roll(text)
                if roll is None:
                    problem_lbl.setText(
                        f"'{text}' isn't an attack roll. Try 17, 12+5 or nat 20."
                    )
                    return None
                rolls[key] = roll
            return rolls

        def do_apply():
            if applied:
                return
            is_attack = roll_combo.currentText() == ATTACK_ROLL
            ability = None if is_attack else ability_combo.currentData()
            typed_condition = name_combo.currentText().strip()
            # "stunned" is Stunned, so the rules see it as they should.
            condition = next(
                (s for s in suggestions if s.lower() == typed_condition.lower()),
                typed_condition,
            )
            damage, problem = read_damage(damage_input.text(), type_combo.currentData())
            if problem:
                problem_lbl.setText(problem)
                return
            pick: EffectOption | None = picked["option"]
            # A pick the source spends (a feature with no numbers) is enough.
            spends = pick is not None and pick.is_tracked and caster is not None
            if (
                not is_attack
                and ability is None
                and not damage
                and not condition
                and not spends
            ):
                problem_lbl.setText("Add a saving throw, damage or a condition.")
                return
            totals = typed_totals() if ability is not None else {}
            attacks = typed_attacks() if is_attack else {}
            if totals is None or attacks is None:
                return
            applied.append(True)
            duration = duration_combo.currentData()
            if duration == "custom":
                unit = CUSTOM_DURATION_UNITS[unit_combo.currentText()]
                duration = {"seconds": amount_input.value() * unit}
            self._custom_save = {
                "roll": roll_combo.currentText(),
                "ability": ability_combo.currentData(),
                "dc": dc_input.value(),
                "half": half_box.isChecked(),
                "bonus": bonus_input.value(),
                "source": source,
            }
            critical_damage = []
            if is_attack:
                critical_damage, _ = read_damage(
                    damage_input.text(), type_combo.currentData(), critical=True
                )
            self._apply_custom_effect(
                CustomEffect(
                    name=name_input.text().strip(),
                    condition=condition,
                    duration=duration,
                    notes=notes_input.text(),
                    damage=damage,
                    critical_damage=critical_damage,
                    count_resistances=resistances_box.isChecked(),
                    slot_level=slot_combo.currentData(),
                    action_cost=action_combo.currentData(),
                    concentration=concentrate_box.isChecked(),
                    attack_bonus=bonus_input.value() if is_attack else None,
                    typed_attacks=attacks,
                    ability=ability,
                    dc=dc_input.value(),
                    mode=mode_combo.currentText(),
                    half_on_save=half_box.isChecked(),
                    use_legendary_resistance=resist_box.isChecked(),
                    repeat_save=repeat_box.isChecked(),
                    typed_totals=totals,
                    pick=pick,
                )
            )
            dlg.accept()

        # The pick, and the damage and search it was made with, to tell the
        # GM's edits by.
        picked: dict = {"option": None, "damage": "", "search": ""}

        def show_duration(seconds: int | None, until: tuple[str, str] | None):
            """Select a pick's duration: a turn, a time, or until removed. A
            turn of a source that isn't there falls back to until removed."""
            index = 0
            if until is not None:
                wanted_turn = {"until": until[0], "of": until[1]}
                index = next(
                    (
                        i
                        for i in range(duration_combo.count())
                        if duration_combo.itemData(i) == wanted_turn
                    ),
                    0,
                )
            elif seconds:
                wanted = {"seconds": seconds}
                index = next(
                    (
                        i
                        for i in range(duration_combo.count())
                        if duration_combo.itemData(i) == wanted
                    ),
                    -1,
                )
                fit = custom_duration(seconds) if index < 0 else None
                if fit is not None:
                    amount_input.setValue(fit[0])
                    unit_combo.setCurrentText(fit[1])
                    index = duration_combo.findData("custom")
            duration_combo.setCurrentIndex(max(index, 0))

        def fill_from(option: EffectOption):
            """Replace everything a pick says with what this one does, and
            clear what it doesn't say. A None DC or bonus keeps the dialog's."""
            picked["option"] = None  # so the slot below isn't taken for an edit
            name_input.setText(option.name)
            note_lbl.setText(option.note)
            note_lbl.setVisible(bool(option.note))
            roll_combo.setCurrentText(option.roll)
            ability_combo.setCurrentIndex(
                max(ability_combo.findData(option.ability), 0) if option.ability else 0
            )
            if option.dc is not None:
                dc_input.setValue(option.dc)
            if option.bonus is not None:
                bonus_input.setValue(option.bonus)
            half_box.setChecked(option.half_on_save)
            repeat_box.setChecked(option.repeat_save)
            # What the source doesn't have (no slot left, no source) is "No ...".
            # findData never finds a PactSlot, and == alone can't tell one
            # from a spell slot of its level.
            slot_combo.setCurrentIndex(
                next(
                    (
                        index
                        for index in range(slot_combo.count())
                        if slot_combo.itemData(index) == option.slot_level
                        and type(slot_combo.itemData(index)) is type(option.slot_level)
                    ),
                    0,
                )
            )
            action_index = action_combo.findData(option.action_cost)
            action_combo.setCurrentIndex(
                max(action_index, 0) if option.action_cost else 0
            )
            concentrate_box.setChecked(option.concentration)
            # A type left from before would disagree with the pick's damage.
            type_combo.setCurrentIndex(0)
            damage = option.damage_at(slot_combo.currentData())
            damage_input.setText(damage)
            name_combo.setCurrentText(option.condition)
            notes_input.clear()
            show_duration(option.duration_seconds, option.until)
            problem_lbl.setText("")
            picked.update(option=option, damage=damage, search=search_box.text())

        def drop_pick(name: str):
            """Typing another name makes it the GM's own effect: nothing is
            spent for the pick, and the slot box no longer upcasts it."""
            option = picked["option"]
            if option is None or name == option.name:
                return
            picked["option"] = None
            tree.clearSelection()
            note_lbl.setText("")
            note_lbl.hide()

        def upcast():
            """A pick's damage at the slot now chosen, unless it's been edited."""
            option = picked["option"]
            if option is None or damage_input.text() != picked["damage"]:
                return
            damage = option.damage_at(slot_combo.currentData())
            damage_input.setText(damage)
            picked["damage"] = damage

        def option_of(item: QTreeWidgetItem | None) -> EffectOption | None:
            """What a row offers: nothing for a category or a greyed row."""
            if item is None or item.isHidden() or item.isDisabled():
                return None
            return item.data(0, Qt.ItemDataRole.UserRole)

        def on_selection_changed():
            items = tree.selectedItems()
            option = option_of(items[0]) if items else None
            if option is not None:
                fill_from(option)

        def first_pickable() -> QTreeWidgetItem | None:
            match = first_visible_item(category_items)
            if match is None or not match.isDisabled():
                return match
            for category in category_items.values():
                for i in range(category.childCount()):
                    if option_of(category.child(i)) is not None:
                        return category.child(i)
            return None

        def search_entered():
            """Enter picks the top match, and then applies what's picked. Once
            the search has changed since the pick, it picks the top match again."""
            current = tree.currentItem()
            option = option_of(current)
            searched = search_box.text() == picked["search"]
            if option is not None and option is picked["option"] and searched:
                do_apply()
                return
            match = first_pickable()
            if match is None:
                return
            again = option_of(match)
            if match is current and again is not None:
                fill_from(again)  # no selection change to do it
            else:
                tree.setCurrentItem(match)

        def item_activated(item: QTreeWidgetItem):
            option = option_of(item)
            if option is None:
                return
            if picked["option"] is not option:
                fill_from(option)
            do_apply()

        tree.itemSelectionChanged.connect(on_selection_changed)
        tree.itemActivated.connect(item_activated)
        search_box.returnPressed.connect(search_entered)
        slot_combo.currentIndexChanged.connect(upcast)
        name_input.textEdited.connect(drop_pick)

        apply_btn.clicked.connect(do_apply)
        name_edit.returnPressed.connect(do_apply)
        notes_input.returnPressed.connect(do_apply)
        damage_input.returnPressed.connect(do_apply)
        name_input.returnPressed.connect(do_apply)
        for total_input in [*typed_inputs.values(), *attack_inputs.values()]:
            total_input.returnPressed.connect(do_apply)
        cancel_btn.clicked.connect(dlg.reject)

        search_box.setFocus()
        dlg.exec()

    @undoable
    def _shortcut_add_concentration(self):
        """Keyboard shortcut 'C': the source starts Concentrating. Self-applied —
        a caster is always the source of their own concentration."""
        if not self.selected_character:
            self._show_status("Nothing applied: left-click a card to pick a source.")
            return
        self._add_condition_to(
            self.selected_character,
            CombatStatus.CONCENTRATING.value,
            source=self.selected_character,
        )

    @undoable
    def _shortcut_remove_concentration(self):
        """Keyboard shortcut 'Ctrl+C': remove Concentrating from the source."""
        if not self.selected_character:
            self._show_status("Nothing removed: left-click a card to pick a source.")
            return
        self._remove_condition_from(
            self.selected_character,
            CombatStatus.CONCENTRATING.value,
            source=self.selected_character,
        )

    @undoable
    def _shortcut_clear_target_conditions(self):
        """Keyboard shortcut 'Ctrl+Shift+C': remove every condition from every target."""
        if not self.target_characters:
            self._show_status("Nothing removed: right-click a card to pick a target.")
            return
        for target in list(self.target_characters):
            for cond in list(target.get("conditions", [])):
                self._remove_condition_from(target, cond)

    @undoable
    def _add_action_use(self, action_type: str, char: dict | None = None):
        """Log a use of Action/Bonus Action/Reaction for char (the source if
        None), this round. Tallies reset when it becomes that combatant's turn
        again (see _advance_turn).
        """
        char = char or self.selected_character
        if not char:
            self._show_status("Nothing logged: left-click a card to pick a source.")
            return
        counts = char.setdefault("action_uses", {})
        counts[action_type] = counts.get(action_type, 0) + 1
        self._log_event(f"{char['name']} uses {action_type}", character=char["name"])
        self._refresh_selected_card()

    @undoable
    def _remove_action_use(self, action_type: str):
        """Correct a mis-logged Action/Bonus Action/Reaction use for the source."""
        if not self.selected_character:
            self._show_status("Nothing logged: left-click a card to pick a source.")
            return
        counts = self.selected_character.setdefault("action_uses", {})
        name = self.selected_character["name"]
        if counts.get(action_type, 0) <= 0:
            self._show_status(f"Nothing refunded: {name} has no {action_type} logged.")
        else:
            counts[action_type] -= 1
            self._log_event(
                f"{self.selected_character['name']} refunds {action_type}",
                character=self.selected_character["name"],
            )
            self._refresh_selected_card()

    @undoable
    def _add_visibility(self):
        if not self.selected_character:
            self._show_status("Nothing applied: left-click a card to pick a source.")
            return
        vis = self.visibility_combo.currentText()
        visibility_states = self.selected_character.get("visibility_states", [])
        if vis not in visibility_states:
            visibility_states.append(vis)
            self._log_event(
                f"{self.selected_character['name']} gains {vis}",
                character=self.selected_character["name"],
                value={"condition": vis},
            )
            self._refresh_selected_card()

    @undoable
    def _remove_visibility(self):
        if not self.selected_character:
            self._show_status("Nothing removed: left-click a card to pick a source.")
            return
        vis = self.visibility_combo.currentText()
        visibility_states = self.selected_character.get("visibility_states", [])
        if vis in visibility_states:
            visibility_states.remove(vis)
            self._log_event(
                f"{self.selected_character['name']} loses {vis}",
                character=self.selected_character["name"],
                value={"condition": vis},
            )
            self._refresh_selected_card()

    @undoable
    def _toggle_hidden_from_players(self, char: dict):
        """Take a monster off the players' screen, or reveal it there, as when
        it joins the fight. The line is logged after the change, so hiding it
        stays the GM's and its appearance is the players' too."""
        if char.pop("hidden_from_players", False):
            text = f"{char['name']} appears"
        else:
            char["hidden_from_players"] = True
            text = f"{char['name']} is hidden from the players"
        self._log_event(text, character=char["name"])
        self._rebuild_card(char)


def _timed_condition_entry(
    cond: str,
    duration: dict | None,
    source: dict | None,
    target: dict,
    turn: list[dict],
) -> dict | None:
    """The char["timed_conditions"] entry that ends `cond` on `target` after
    `duration` (see CUSTOM_CONDITION_DURATIONS), given during `turn` (whose
    turn it is: [] outside combat). None when it lasts until removed."""
    if duration is None:
        return None
    if "seconds" in duration:
        return {
            "name": cond,
            "time_left": duration["seconds"],
            "duration": duration["seconds"],
            "ticks_on": turn[0]["name"] if turn else None,
        }
    whose = source if duration["of"] == "source" else target
    if whose is None:
        return None
    until = duration["until"]
    # The end of `whose` next turn is the end of the one after this, if this
    # is their turn; the start of their next turn is always the first to come.
    taking_turn = any(c is whose for c in turn)
    return {
        "name": cond,
        "until": until,
        "of": whose["name"],
        "turns_left": 2 if until == "end" and taking_turn else 1,
        "text": f"Until the {until} of {whose['name']}'s next turn",
    }
