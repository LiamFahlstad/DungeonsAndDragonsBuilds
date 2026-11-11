"""Conditions mixin for CombatAppQt."""

import re
from dataclasses import replace
from html import escape

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTextBrowser,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import Action, CombatStatus
from Combat.Effects.active_effects import (
    CUSTOM,
    FEATURE,
    SPELL,
    ActiveEffect,
    active_effects,
    describe,
    drop_repeat_save,
    duration_entry,
    give_modifiers,
    link_concentration,
    note_origin,
    remove_effect,
    repeat_saves,
    set_duration,
    set_repeat_save,
    tick,
)
from Combat.Effects.modifiers import (
    RollPlan,
    armor_class_notes,
    attack_plan,
    bonus_reminder,
    cover,
    extra_text,
    hit_extras,
    hit_plan,
    hit_point_maximum,
    hit_point_maximum_notes,
    rolled_modifiers,
    rules_condition,
    signed,
)
from Model.Content.CombatModifiers import Modifier
from Combat.Effects.triggers import AttackOutcome, reduced_damage
from Combat.WildShape import current_form, form_badge
from Core.Definitions import Condition, DamageType
from Core.Rules import SECONDS_PER_ROUND
from Model.Content.CombatModifiers import AttackKind
from Model.Content.RulesConditions import conditions_with
from .amounts import AmountError, parse_amount
from .attack_rolls import (
    AttackRoll,
    armor_bonus,
    armor_in_use,
    cover_bonus,
    parse_attack_roll,
)
from .effect_dialog_widgets import (
    SearchKeys,
    chip,
    chip_row,
    row_widget,
    section,
    target_roll_rows,
)
from .effect_options import (
    COLLAPSED_CATEGORIES,
    amount_text as _amount_text,
    effect_options,
    spell_slot_choices,
)
from .features_mixin import FEATURE_BADGE_COLOR
from .monster_actions import first_number, legendary_resistances_left, roll_dice
from .player_view import note_condition_immunity
from .resources import feature_lack, monster_action_lack, spell_slot_lack
from .saves import (
    ABILITIES,
    AMOUNT_KINDS,
    ATTACK_ROLL,
    CONDITION_JOINER,
    DAMAGE_AMOUNT,
    DEFAULT_SAVE_DC,
    FEATURE,
    HEALING,
    MONSTER_ACTION,
    ROLL_MODES,
    SAVING_THROW,
    SPELL,
    TEMP_HP,
    CustomEffect,
    EffectOption,
    condition_names,
    is_immune_to,
    known_attack_bonus,
    known_save_dc,
    read_damage,
    read_hit_points,
    roll_extra_damage,
    roll_planned_attack,
    roll_save,
    rolled_damage,
    save_modifier,
    save_reminder,
    with_extra_damage,
)
from .spells_mixin import spell_badge_color, spell_badge_description
from .stats import _default_stats, increment_named_stat
from .state import CombatWindowState
from .styles import QSS
from .tree_filter import filter_category_tree, first_visible_item
from .undo import undoable

# The conditions that give Incapacitated, which breaks Concentration (and
# ends a Wild Shape form): Paralyzed, Petrified, Stunned, Unconscious too.
_INCAPACITATING = conditions_with(Condition.INCAPACITATED)


def incapacitates(name: str) -> bool:
    """Whether a condition named `name` gives Incapacitated, also under a
    longer custom name ("Stunned by Stunning Strike")."""
    return rules_condition(name) in _INCAPACITATING


# What a hit made with a weapon's row (True) or an Unarmed Strike's (False)
# is, for its triggers; None: not known.
_ATTACK_KINDS: dict[bool | None, AttackKind | None] = {
    True: AttackKind.WEAPON,
    False: AttackKind.UNARMED,
    None: None,
}


def _picked_effect(option: EffectOption, last_save: dict) -> CustomEffect | None:
    """What the Custom Effect dialog applies for `option` picked and nothing
    edited: its roll, damage rolled now (twice over for a Critical Hit),
    conditions, duration and costs. A DC or attack bonus it leaves unset is
    the dialog's last (`last_save`, ConditionsMixin._custom_save). None when
    its damage can't be applied as it is (a damage type to choose)."""
    is_attack = option.roll == ATTACK_ROLL
    text = option.damage_at(option.slot_level)
    damage: list[tuple[int, str]] = []
    critical: list[tuple[int, str]] = []
    hit_points = 0
    if option.amount_kind == DAMAGE_AMOUNT:
        damage, problem = read_damage(text)
        if is_attack and not problem:
            critical, problem = read_damage(text, critical=True)
    else:
        hit_points, problem = read_hit_points(text, option.amount_kind)
    if problem:
        return None
    duration: dict | None = None
    if option.until is not None:
        duration = {"until": option.until[0], "of": option.until[1]}
    elif option.duration_seconds:
        duration = {"seconds": option.duration_seconds}
    dc = option.dc if option.dc is not None else last_save.get("dc")
    bonus = option.bonus if option.bonus is not None else last_save.get("bonus")
    return CustomEffect(
        name=option.name,
        condition=option.condition,
        duration=duration,
        damage=damage,
        critical_damage=critical,
        healing=hit_points if option.amount_kind == HEALING else 0,
        temp_hp=hit_points if option.amount_kind == TEMP_HP else 0,
        slot_level=option.slot_level,
        action_cost=option.action_cost,
        concentration=option.concentration,
        attack_bonus=(bonus or 0) if is_attack else None,
        ability=None if is_attack else option.ability,
        dc=dc if dc is not None else DEFAULT_SAVE_DC,
        half_on_save=option.half_on_save,
        repeat_save=option.repeat_save,
        pick=option,
        weapon_attack=option.weapon_attack,
    )


# The durations the Custom Condition dialog offers, as (label, duration). A
# duration is None (until removed), {"seconds": n} (counted down a round at a
# time, on the turn it was given in), or {"until": "start" | "end", "of":
# "source" | "target"} (ends at the start or end of the source's, or each
# target's, next turn), or {"until": "end", "of": "current"} (ends as the
# turn being taken ends). "{source}" in a label is the source's name.
CUSTOM_CONDITION_DURATIONS: list[tuple[str, dict | None]] = [
    ("Until removed", None),
    ("Until the end of this turn", {"until": "end", "of": "current"}),
    ("Until the start of {source}'s next turn", {"until": "start", "of": "source"}),
    ("Until the end of {source}'s next turn", {"until": "end", "of": "source"}),
    ("Until the start of the target's next turn", {"until": "start", "of": "target"}),
    ("Until the end of the target's next turn", {"until": "end", "of": "target"}),
    ("1 round (6 seconds)", {"seconds": SECONDS_PER_ROUND}),
    ("1 minute (10 rounds)", {"seconds": 60}),
    ("10 minutes", {"seconds": 10 * 60}),
    ("1 hour", {"seconds": 60 * 60}),
]

# The Custom Effect dialog: as wide as the screen allows up to the preferred
# width, never narrower than the minimum, which the chip rows need.
_CUSTOM_DIALOG_WIDTH = 1040
_PREFERRED_DIALOG_WIDTH = 1200
_SCREEN_MARGIN = 60
_PICKER_WIDTH = 340
_SUMMARY_WIDTH = 150  # a picker row's numbers ("+6  1d8 + 4 Slashing")
_SUMMARY_COLOR = "#9fb4d0"
# A row the source is out of (spent, too few legendary actions left).
_UNAVAILABLE_COLOR = "#6a6a7a"
_DETAILS_MIN_HEIGHT = 90
_BUTTON_WIDTH = 110
# The roll kind with neither a saving throw nor an attack roll.
NO_ROLL = "No roll"
# The amount box's title and hint, for what it holds.
_AMOUNT_TITLES = {
    DAMAGE_AMOUNT: "Damage",
    HEALING: "Healing (every target)",
    TEMP_HP: "Temporary Hit Points (every target)",
}
_AMOUNT_HINTS = {
    DAMAGE_AMOUNT: "e.g. 8d6, 28, 2d6 sl + 1d4 fi",
    HEALING: "e.g. 2d8 + 3, 10",
    TEMP_HP: "e.g. 2d4 + 4, 5",
}
_DETAILS_HINT = (
    "<p style='color:#a0a0b0'>Pick what was used and it fills in the form;"
    " its rules text shows here. Or fill in the form by hand.</p>"
    "<p style='color:#a0a0b0'><b>↑/↓</b> browse · <b>Enter</b> picks the top"
    " match, <b>Enter</b> again applies · <b>Esc</b> empties the search</p>"
)
_NATURAL_ROLL = re.compile(r"nat(?:ural)?\s*\d+", re.IGNORECASE)
_WHOLE_NUMBER = re.compile(r"-?\d+")
MAX_SAVE_DC = 40
MIN_ATTACK_BONUS = -10
MAX_ATTACK_BONUS = 30
# The most times one Apply repeats an effect (Scorching Ray at a level 9
# slot has 10 rays).
MAX_EFFECT_TIMES = 20
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
    where = _where_from(option)
    source = f"<i>{where}</i><br>" if where else ""
    return f"<b>{escape(option.row_text, quote=False)}</b><br>{source}{text}"


def _where_from(option: EffectOption) -> str:
    """Where a spell's or feature's pick got its numbers, or "" for an attack
    or a monster's action, whose numbers are its own."""
    if option.kind == SPELL:
        if option.is_described:
            return "Filled in from checked spell data."
        return "Read from its rules text: check the form."
    if option.kind == FEATURE:
        of = ""
        if option.feature_name and option.feature_name != option.name:
            of = f"{escape(option.feature_name, quote=False)}: "
        if option.is_described:
            return f"{of}filled in from the feature's combat data."
        return f"{of}read from its rules text: check the form."
    action = option.monster_action
    if option.kind == MONSTER_ACTION and option.is_described and action is not None:
        of = ""
        if action.name != option.name:
            of = f"{escape(action.name, quote=False)}: "
        return f"{of}filled in from the stat block's combat data."
    return ""


def _option_details(option: EffectOption) -> str:
    """The Custom Effect dialog's rules text pane for a pick: its name, its
    numbers, where its numbers came from, and its rules text."""
    name = escape(option.row_name or option.name, quote=False)
    lines = [f"<p style='margin:0'><b style='color:#c9a84c'>{name}</b></p>"]
    if option.summary:
        summary = escape(option.summary, quote=False)
        lines.append(f"<p style='margin:0;color:{_SUMMARY_COLOR}'>{summary}</p>")
    where = _where_from(option)
    if where:
        lines.append(f"<p style='margin:0;color:#a0a0b0'><i>{where}</i></p>")
    if option.tooltip:
        text = escape(option.tooltip, quote=False).replace("\n", "<br>")
        lines.append(f"<p style='margin-top:6px'>{text}</p>")
    return "".join(lines)


def _who_text(source: dict | None, targets: list[dict]) -> str:
    """The Custom Effect dialog's first line: the source, then its targets."""
    names = ", ".join(escape(t["name"], quote=False) for t in targets)
    on = f"<span style='color:#e74c3c'>{names}</span>"
    if source is None:
        return f"<span style='color:#a0a0b0'>No source</span> → {on}"
    who = escape(source["name"], quote=False)
    return f"<span style='color:#c9a84c'>{who}</span> → {on}"


def _armor_text(target: dict) -> str:
    """What an attack roll against target has to meet: "AC 15", with its
    cover in it ("AC 17 (cover)"), or "AC ?" when that isn't known."""
    armor = first_number(target.get("ac"))
    if armor is None:
        return "AC ?"
    armor += armor_bonus(target)
    return f"AC {armor} (cover)" if cover_bonus(target) else f"AC {armor}"


def _bonus_notes(plan: RollPlan) -> list[str]:
    """What adds to a roll, for a tooltip: "Bless: +1d4"."""
    return [f"{label}: {signed(amount)}" for label, amount in plan.bonuses]


def _attack_text(source: dict | None, target: dict) -> str:
    """A target's row for an attack roll: what it has to meet, the mode the
    modifiers give it and what they add to it, to roll it that way at the
    table ("AC 15, Advantage", "AC 15, +1d4 to hit"). The extra damage a hit
    on it deals has a row of its own under it (target_roll_rows' extras)."""
    plan = attack_plan(source, target, "Neutral")
    parts = [_armor_text(target)]
    if plan.mode != "Neutral":
        parts.append(plan.mode)
    flat, dice = bonus_reminder(plan)
    added = " ".join(p for p in (f"{flat:+d}" if flat else "", dice) if p)
    if added:
        parts.append(f"{added} to hit")
    return ", ".join(parts)


def _attack_tooltip(source: dict | None, target: dict) -> str:
    plan = attack_plan(source, target, "Neutral")
    extras = [f"{label}: {extra_text(m)}" for label, m in hit_extras(source, target)]
    if extras:
        extras.append(
            "Rolled and added to a hit's damage, or typed in its box on this"
            " row if rolled at the table. A damage total typed in has it"
            " already, unless it's typed in its box."
        )
    return "\n".join(
        [
            "What the attack roll has to meet, cover included",
            *armor_class_notes(target),
            *plan.notes,
            *_bonus_notes(plan),
            *extras,
        ]
    )


def _save_text(target: dict, ability: str) -> str:
    """A target's row for a saving throw: its bonus with what its modifiers
    add, and what they do to the roll, to roll it that way at the table
    ("DEX +3, Disadvantage", "DEX +5 (cover)", "WIS +1 +1d4", "DEX fails")."""
    plan = save_reminder(target, ability)
    if plan.auto_fail:
        return f"{ability} fails"
    flat, dice = bonus_reminder(plan)
    text = f"{ability} {save_modifier(target, ability) + flat:+d}"
    if dice:
        text = f"{text} {dice}"
    if any(label == cover(target) for label, _ in plan.bonuses):
        text = f"{text} (cover)"
    return text if plan.mode == "Neutral" else f"{text}, {plan.mode}"


def _save_tooltip(target: dict, ability: str) -> str:
    plan = save_reminder(target, ability)
    why = [plan.auto_fail] if plan.auto_fail else [*plan.notes, *_bonus_notes(plan)]
    return "\n".join([f"{target['name']}'s {ability} saving throw bonus", *why])


def _damage_preview(text: str, chosen_type: str | None) -> str:
    """The damage typed, for the preview line, with the dropdown's type when
    the text names none. Nothing is rolled."""
    text = text.strip()
    if not text:
        return ""
    try:
        parts = rolled_damage(_DICELESS.sub("1", text))
    except AmountError:
        return f"{text} (can't be read)"
    if chosen_type is None or all(damage_type for _, damage_type in parts):
        return text
    return f"{text} {chosen_type}"


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def _effect_dialog_width(window: QWidget | None) -> int:
    """The Custom Effect dialog's width on the window's screen."""
    screen = window.screen() if window is not None else None
    if screen is None:
        return _CUSTOM_DIALOG_WIDTH
    room = screen.availableGeometry().width() - _SCREEN_MARGIN
    return max(_CUSTOM_DIALOG_WIDTH, min(_PREFERRED_DIALOG_WIDTH, room))


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
                incapacitates(cond)
                and cond != "Concentrating"
                and "Concentrating" in char.get("conditions", [])
            ):
                self._remove_condition_from(char, "Concentrating", source=char)
            # So does a Wild Shape form (which a knock-out's Unconscious ends too).
            if incapacitates(cond) and current_form(char):
                self._leave_wild_shape(char, reason=cond)

    def _give_badge_modifiers(
        self,
        char: dict,
        name: str,
        modifiers,
        *,
        levels_up: int = 0,
        source: dict | None = None,
    ):
        """char's badge `name` gives `modifiers` while it's on, their dice
        rolled now (rolled_modifiers). One that raises its Hit Point maximum
        raises its current Hit Points by as much (Aid: "Hit Point maximum and
        current Hit Points increase by 5"), as Hit Points regained from
        `source`, so a creature at 0 HP comes to; one that lowers it leaves
        no more than the new maximum."""
        before = hit_point_maximum(char)
        kept: tuple[Modifier, ...] = rolled_modifiers(modifiers, levels_up, roll_dice)
        give_modifiers(char, name, kept)
        change = hit_point_maximum(char) - before
        if not change:
            return
        notes = ", ".join(hit_point_maximum_notes(char))
        self._log_event(
            f"{char['name']}'s Hit Point maximum is {hit_point_maximum(char)}"
            f" ({char['max_hp']}, {notes})",
            character=char["name"],
        )
        if change > 0:
            # _heal_target sees to Bloodied by the new maximum.
            self._heal_target(char, change, source)
        else:
            self._keep_hit_points_in_maximum(char, name)

    def _keep_hit_points_in_maximum(self, char: dict, reason: str):
        """char has no more Hit Points than its maximum, now that `reason`
        changed it (Aid ending), logged so the party's history replays it.
        Bloodied goes by the new maximum."""
        top = hit_point_maximum(char)
        if char["hp"] > top:
            lost = char["hp"] - top
            char["hp"] = top
            self._log_event(
                f"{char['name']} has {top} HP, the most its Hit Point maximum"
                f" allows without {reason}",
                character=char["name"],
                action=Action.LOSE_HIT_POINTS,
                value={
                    "hp_delta": -lost,
                    "reason": reason,
                    "target_name": char["name"],
                },
            )
        self._apply_bloodied_condition(char, source=char)

    @undoable
    def _remove_condition_from(self, char: dict, cond: str, source: dict | None = None):
        if cond in char["conditions"]:
            # What it did to the Hit Point maximum (Aid) goes with it.
            maximum = hit_point_maximum(char)
            char["conditions"].remove(cond)
            # Its tooltip, colour, timer and repeat save go with it.
            remove_effect(char, cond)
            if hit_point_maximum(char) != maximum:
                self._keep_hit_points_in_maximum(char, cond)
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
            if cond == CombatStatus.CONCENTRATING.value:
                char.pop("concentration_checks", None)
                self._end_concentration_spells(char)
            # Taking the Wild Shape badge off is leaving the form early. The
            # badge is gone already, so the form goes too, without asking.
            form = current_form(char)
            if form is not None and cond == form_badge(form):
                self._leave_wild_shape(char, ask=False)
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
        source_name = source["name"] if source is not None else None
        turn = [c["name"] for c in self._current_turn_group()]
        for target in list(targets):
            if notes.strip():
                describe(target, cond, notes.strip(), None, CUSTOM)
            self._add_condition_to(target, cond, source=source)
            set_duration(
                target,
                cond,
                duration_entry(duration, source_name, target["name"], turn),
            )
            note_origin(target, cond, caster=source_name)
            self._rebuild_card(target)
        self._save_fight_state()

    def _tick_effect_durations(
        self, ended: list[dict], started: list[dict], new_round: bool
    ):
        """Count the effects' durations down as the turn passes from `ended`
        to `started` (`new_round` when that begins a round), ending each one
        whose time or turns run out."""
        ended_names = {c["name"] for c in ended}
        started_names = {c["name"] for c in started}
        in_order = {c["name"] for c in self.initiative_order}
        for char in self.characters:
            effects = active_effects(char)
            if not any(e["duration"] is not None for e in effects):
                continue
            for effect in list(effects):
                duration = effect["duration"]
                if duration is None:
                    continue
                if tick(duration, ended_names, started_names, new_round, in_order):
                    self._log_event(
                        f"{char['name']}'s {effect['name']} expires",
                        note_turn=False,
                        character=char["name"],
                    )
                    self._remove_condition_from(char, effect["name"])
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
        """Apply a Custom dialog effect to every living target
        (_apply_effect_to_targets), then ask about what its hits trigger
        (Hill's Tumble), in the same undo step. A pick that goes on its user
        (Second Wind: targets_self) goes on the source alone, whoever is
        targeted; the targets stay as they were."""
        owner = self.selected_character or self._current_turn_character()
        if effect.pick is not None and effect.pick.targets_self and owner is not None:
            targets, saved_targets = self.target_characters, self._saved_targets
            self.target_characters, self._saved_targets = [owner], []
            try:
                with self._one_trigger_prompt():
                    self._apply_effect_to_targets(effect)
            finally:
                self.target_characters, self._saved_targets = targets, saved_targets
                self._update_target_label()
            return
        with self._one_trigger_prompt():
            self._apply_effect_to_targets(effect)

    def _apply_effect_to_targets(self, effect: CustomEffect):
        """Apply a Custom dialog effect to every living target: what it costs
        the source, then with an attack roll, the source rolls against each
        one's AC: a hit takes it all, a critical hit with the dice rolled twice
        over, and a miss takes nothing. With a saving throw, each one rolls, and
        a save halves the damage (or avoids it) and avoids the condition. With
        neither, everyone takes it all, except those marked ½ Saved, who saved
        by hand and count the same. Healing and Temporary Hit Points go to
        every target first, whatever the roll."""
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
            pick = effect.pick
            if (
                pick is not None
                and pick.kind == SPELL
                and pick.counts_uses
                and not self._can_cast_or_say(caster, pick.spell_name or pick.name)
            ):
                return
            if not self._go_ahead_anyway(
                caster, f"Use {label}", self._effect_lacks(caster, effect)
            ):
                return
            if pick is not None:
                used = self._use_pick(caster, effect)
                if used is None:
                    return
                logged_use = used
            if effect.slot_level is not None:
                self._cast_spell_slot_level(effect.slot_level)
            if effect.action_cost is not None:
                self._add_action_use(effect.action_cost, ask=False)
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
        # What a hit's triggers are told about the attack (Combat/Effects/
        # triggers.py): a weapon's or an Unarmed Strike's, and the row.
        kind = _ATTACK_KINDS.get(effect.weapon_attack)
        picked_row = effect.pick.name if effect.pick is not None else effect.row
        for target in living:
            # Hit Points go to every target, whatever the roll decides.
            if effect.healing:
                self._heal_target(target, effect.healing, source)
            if effect.temp_hp:
                self._give_temp_hp(target, effect.temp_hp, source)
            saved = any(target is s for s in self._saved_targets)
            damage = effect.damage
            hit: bool | None = None
            critical = False
            if effect.attack_bonus is not None:
                # The attacker's and the target's conditions count in a roll
                # made here; one typed in gets what it couldn't count.
                typed = effect.typed_attacks.get(id(target))
                plan = attack_plan(source, target, effect.mode, typed is not None)
                if typed is not None:
                    roll, notes = typed, plan.notes
                else:
                    roll, notes = roll_planned_attack(effect.attack_bonus, plan)
                hit, attack = self._resolve_attack_roll(target, roll, source, notes)
                reduction = 0
                if hit is not False and source is not None:
                    # What the target answers the hit with (Shield, Deflect
                    # Attacks), before its damage.
                    still, reduction = self._before_hit(
                        AttackOutcome(
                            source,
                            target,
                            hit,
                            critical=roll.is_critical,
                            kind=kind,
                            row=picked_row,
                            total=roll.total,
                            armor=armor_in_use(target),
                        )
                    )
                    if not still:
                        hit = False
                        attack = f"{attack}, then a miss"
                results.append(hit is not False)
                attacks.append(attack)
                if hit is False:
                    if source is not None:
                        self._after_attack(
                            AttackOutcome(
                                source,
                                target,
                                False,
                                kind=kind,
                                row=picked_row,
                                damage_dealt=0,
                            )
                        )
                    continue
                saved = False
                critical = roll.is_critical
                if roll.is_critical:
                    damage = effect.critical_damage or damage
                if damage:
                    damage = self._with_hit_extras(
                        source, target, damage, effect, roll.is_critical
                    )
                if reduction:
                    damage = reduced_damage(damage, reduction)
            if effect.ability is not None:
                saved = self._roll_effect_save(target, effect)
                results.append(saved)
            avoided = effect.ability is not None and saved and not effect.half_on_save
            dealt = 0
            if damage and not avoided:
                dealt = self._deal_damage(
                    target, damage, source, effect.count_resistances, saved
                )
                if not any(c is target for c in self.characters):
                    continue  # a summon that vanished at 0 HP
            if effect.attack_bonus is not None and source is not None:
                # What the hit triggers is asked once the Apply is done.
                self._after_attack(
                    AttackOutcome(
                        source,
                        target,
                        hit,
                        critical=critical,
                        kind=kind,
                        row=picked_row,
                        damage_dealt=dealt,
                    )
                )
            if saved:
                continue
            # What it ends (Lay on Hands' Poisoned) goes from the same targets
            # its conditions would land on.
            for condition in effect.pick.ends_conditions if effect.pick else ():
                if condition in target["conditions"]:
                    self._remove_condition_from(target, condition, source=source)
            for condition in effect.conditions:
                row = {"target": target["name"], "condition": condition}
                already_had = condition in target["conditions"]
                held_by_a_spell = self._held_by_effect(row)
                if self._give_effect_condition(target, effect, condition):
                    if held_by_a_spell or not already_had:
                        applied.append(row)
            if effect.repeat_save and effect.ability is not None:
                self._track_repeat_save(target, effect)

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

    def _with_hit_extras(
        self,
        source: dict | None,
        target: dict,
        damage: list[tuple[int, str]],
        effect: CustomEffect,
        critical: bool,
    ) -> list[tuple[int, str]]:
        """A hit's damage with the extra damage that comes with it (Hunter's
        Mark's on its caster's hits, Divine Favor's on its caster's weapon
        hits), rolled after the attack's own dice, doubled for a Critical
        Hit. The log says what each adds, and what wasn't counted. One
        rolled at the table (its box under Damage) is added as typed, even
        to a typed damage total; a typed total gets none rolled here, as it
        was all rolled at the table (Decision 4)."""
        rolled = effect.typed_extras.get(id(target), {})
        plan = hit_plan(source, target, effect.weapon_attack, rolled)
        in_total: list[str] = []
        if effect.typed_damage:
            in_total = [
                f"{label}: not rolled, as the damage total typed has it"
                for label, _, _ in plan.extras
                if label not in plan.at_table
            ]
            plan = replace(
                plan,
                extras=tuple(e for e in plan.extras if e[0] in plan.at_table),
                notes=(),
            )
        extra, lines = roll_extra_damage(plan, critical)
        for line in (*lines, *plan.notes, *in_total):
            # After the hit's line, for the GM only: the player link joins a
            # hit's damage to its line, which a line between would stop.
            self._log_event(line, character=target["name"], public=False)
        return with_extra_damage(damage, extra)

    @undoable
    def _apply_custom_effects(self, effects: list[CustomEffect]):
        """Several Custom dialog effects as one step (the rays of one
        Scorching Ray): undone together, and what their hits trigger asked
        about once (Q41)."""
        with self._one_trigger_prompt():
            for effect in effects:
                self._apply_custom_effect(effect)

    def _apply_row(self, owner: dict, target: dict, option: EffectOption) -> bool:
        """Use one picker row of owner's on target, as picking it in the
        Custom Effect dialog and applying it as it's filled in would: what
        it costs (a use, logged), its roll, damage and conditions. What a
        hit triggers comes this way (TurnPanelMixin._use_trigger). Returns
        whether it was applied: not if owner is out of what it spends (no
        uses left, the action used), which the caller says."""
        effect = _picked_effect(option, self._custom_save)
        if effect is None or any(self._effect_lacks(owner, effect)):
            return False
        if option.note:
            # No dialog shows its note, so what it gives carries it (a
            # grapple's escape DC).
            effect = replace(effect, notes=option.note)
        source, targets = self.selected_character, self.target_characters
        saved_targets = self._saved_targets
        self.selected_character, self.target_characters = owner, [target]
        self._saved_targets = []
        try:
            self._apply_custom_effect(effect)
        finally:
            self.selected_character, self.target_characters = source, targets
            self._saved_targets = saved_targets
            self._update_target_label()
        return True

    def _use_pick(self, caster: dict, effect: CustomEffect) -> bool | None:
        """Count what the dialog's pick was as used by caster, as Cast Spell,
        Enable Feature and the turn column's buttons do. Returns whether that
        logged its use, or None, having said why, if it can't be used now."""
        option = effect.pick
        assert option is not None  # the caller checks
        if option.kind == SPELL:
            if not option.counts_uses:
                return False  # part of a cast already counted (Ice Knife's burst)
            spell = option.spell_name or option.name
            if not self._can_cast_or_say(caster, spell):
                return None
            self._count_spell_cast(caster, spell, option.spell_level, effect.slot_level)
            return True
        if option.kind == FEATURE:
            self._count_feature_use(
                caster, option.feature_name or option.name, option.counts_uses
            )
            return True
        if option.monster_action is not None:
            # _apply_custom_effect asked already if it's spent (_effect_lacks).
            return self._spend_monster_action(caster, option.monster_action, ask=False)
        return False

    def _effect_lacks(self, caster: dict, effect: CustomEffect) -> list[str | None]:
        """What caster is out of that the effect spends: its pick's slot,
        uses or recharge, and its action."""
        lacks = [self._action_lack(caster, effect.action_cost)]
        option = effect.pick
        if option is None:
            return lacks
        if option.kind == SPELL and option.counts_uses:
            lacks.insert(
                0, spell_slot_lack(caster, option.spell_level, effect.slot_level)
            )
        elif option.kind == FEATURE and option.counts_uses:
            lacks.insert(0, feature_lack(caster, option.feature_name or option.name))
        elif option.monster_action is not None:
            lacks.insert(0, monster_action_lack(caster, option.monster_action))
        return lacks

    def _effect_picker(
        self, source: dict | None
    ) -> tuple[QLineEdit, QTreeWidget, dict[str, QTreeWidgetItem]]:
        """The Custom Effect dialog's search box and list of what the source
        can use (effect_options), by category: a row's name, then its numbers.
        What the source is out of now is greyed out, but can still be
        picked: applying it asks first (_go_ahead_anyway)."""
        search_box = QLineEdit()
        search_box.setObjectName("effectSearch")
        search_box.setPlaceholderText("Search attacks, spells, features…")
        search_box.setClearButtonEnabled(True)
        search_box.setToolTip(
            "Type part of a name. ↑/↓ move through the list, Enter picks the"
            " top match and Enter again applies it. Esc empties the search."
        )
        tree = QTreeWidget()
        tree.setObjectName("effectOptions")
        tree.setHeaderHidden(True)
        tree.setColumnCount(2)
        tree.setUniformRowHeights(True)
        tree.setTextElideMode(Qt.TextElideMode.ElideRight)
        header = tree.header()
        assert header is not None  # a tree always has one
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        tree.setColumnWidth(1, _SUMMARY_WIDTH)
        summary_color = QColor(_SUMMARY_COLOR)
        unavailable_color = QColor(_UNAVAILABLE_COLOR)
        category_items: dict[str, QTreeWidgetItem] = {}
        for title, options in effect_options(source, self._all_spells()):
            category = QTreeWidgetItem([title])
            category.setFirstColumnSpanned(True)
            tree.addTopLevelItem(category)
            category_items[title] = category
            for option in options:
                item = QTreeWidgetItem([option.row_name or option.name, option.summary])
                item.setData(0, Qt.ItemDataRole.UserRole, option)
                tooltip = _option_tooltip(option)
                item.setToolTip(0, tooltip)
                item.setToolTip(1, tooltip)
                if option.is_unavailable:
                    # Still the GM's to pick: applying it asks first.
                    item.setForeground(0, unavailable_color)
                    item.setForeground(1, unavailable_color)
                else:
                    item.setForeground(1, summary_color)
                category.addChild(item)
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
        self._link_concentration(caster, applied)
        self._rebuild_card(caster)

    def _link_concentration(self, caster: dict, applied: list[dict]):
        """Record on each effect in `applied` ({"target", "condition"} rows,
        as an active spell holds them) that caster concentrates on it."""
        for row in applied:
            target = self._find_character_by_name(row["target"])
            if target is not None:
                link_concentration(target, row["condition"], caster["name"])

    def _give_effect_condition(
        self, target: dict, effect: CustomEffect, condition: str
    ) -> bool:
        """Give target one of the effect's conditions, unless it's died of
        the effect or is immune. Returns whether it has it from this effect
        now."""
        if self._char_death_state(target) == "dead":
            return False
        if is_immune_to(target, condition):
            readable = self._log_event(
                f"{target['name']} is immune to {condition}",
                character=target["name"],
            )
            if readable:
                note_condition_immunity(target, condition)
            return False
        self._describe_effect_condition(target, effect, condition)
        self._add_custom_condition(condition, effect.duration, effect.notes, [target])
        note_origin(target, condition, source=effect.name)
        if effect.pick is not None:
            # Who gave it, also on a record only its modifiers made: extra
            # damage from its caster's hits (Hunter's Mark) goes by it.
            source = self.selected_character or self._current_turn_character()
            levels_up = max(
                (effect.slot_level or effect.pick.spell_level)
                - effect.pick.spell_level,
                0,
            )
            self._give_badge_modifiers(
                target,
                condition,
                effect.pick.modifiers_for(condition),
                levels_up=levels_up,
                source=source,
            )
            if source is not None:
                note_origin(
                    target, condition, source=effect.name, caster=source["name"]
                )
        return True

    def _track_repeat_save(self, target: dict, effect: CustomEffect):
        """The save target repeats at the end of each of its turns, ending
        every condition the effect gave it: one save for them all (Turn
        Undead's Frightened and Incapacitated)."""
        given = [c for c in effect.conditions if c in target["conditions"]]
        if not given or effect.ability is None:
            return
        first, *also = given
        set_repeat_save(
            target,
            first,
            effect.ability,
            effect.dc,
            effect.mode,
            effect.use_legendary_resistance,
            also,
        )
        note_origin(target, first, source=effect.name)

    def _describe_effect_condition(self, target: dict, effect: CustomEffect, cond: str):
        """What target's badge for the effect's condition shows when clicked
        or hovered: the picked spell's card, as Cast Spell's badge has, the
        picked feature's, or the rules text of the attack or action picked.
        Notes typed in the dialog come first. Nothing for an effect typed in
        by hand, whose badge shows its notes, if any."""
        option = effect.pick
        if option is None:
            return
        notes = escape(effect.notes.strip(), quote=False)
        notes = f"<i>{notes}</i><br><br>" if notes else ""
        # A spell's card, for a spell or a feature's use that casts one.
        spell_name = option.spell_name or (option.name if option.kind == SPELL else "")
        if spell_name:
            spell = self._spell_named(spell_name)
            if spell is not None:
                describe(
                    target,
                    cond,
                    notes + spell_badge_description(spell),
                    spell_badge_color(spell),
                    SPELL,
                )
                return
        owner = self.selected_character or self._current_turn_character()
        if option.kind == FEATURE and owner is not None:
            feature = next(
                (
                    f
                    for f in owner.get("_feature_objects", [])
                    if f.name == (option.feature_name or option.name)
                ),
                None,
            )
            if feature is not None:
                describe(
                    target,
                    cond,
                    notes + self._feature_condition_tooltip(owner, feature),
                    FEATURE_BADGE_COLOR,
                    FEATURE,
                )
                return
        if option.tooltip:
            # A weapon's or a monster's action: its name and rules text.
            name = escape(option.row_name or option.name, quote=False)
            text = escape(option.tooltip, quote=False).replace("\n", "<br>")
            describe(
                target,
                cond,
                f"{notes}<b style='color:#c9a84c; font-size:14px;'>{name}</b>"
                f"<br><br>{text}",
                None,
                FEATURE,
            )

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

    def _end_of_turn_saves(self, char: dict):
        """As char's turn ends, the saves that could end a condition on it. A
        monster rolls, keeping the roll if the turn is undone and passed again;
        a player rolls at the table, so they get a reminder, as a monster does
        with the setting monsters_roll_turn_dice off."""
        if self._char_death_state(char) == "dead":
            return
        for effect in list(repeat_saves(char)):
            condition = effect["name"]
            if condition not in char["conditions"]:
                drop_repeat_save(char, condition)
                continue
            entry = effect["repeat_save"]
            if entry is None:
                continue  # dropped by an earlier save this turn
            ability = next(f for f, short in ABILITIES if short == entry["ability"])
            if char.get("_is_player") or not self.settings.monsters_roll_turn_dice:
                self._turn_start_notes.append(
                    f"{char['name']}: DC {entry['dc']} {ability} save to end {condition}"
                )
                continue
            self._roll_repeat_save(char, effect, ability)

    def _roll_repeat_save(self, char: dict, effect: ActiveEffect, ability: str):
        """A monster's save to end a condition (effect's repeat save), and
        what comes of it."""
        condition = effect["name"]
        entry = effect["repeat_save"]
        assert entry is not None  # the caller checks
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
            ended = [condition, *entry.get("also", ())]
            self._log_event(
                f"{name} ends {' and '.join(ended)} with a DC {entry['dc']}"
                f" {ability} save{rolled}{note}",
                character=name,
            )
            for each in ended:
                if each in char["conditions"]:
                    self._remove_condition_from(char, each)
            self._turn_start_notes.append(
                f"{name} saved{rolled}: {' and '.join(ended)} ends"
            )
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
        if effect.healing:
            words.append(f"heals {effect.healing}")
        if effect.temp_hp:
            words.append(f"{effect.temp_hp} temp HP")
        if effect.condition:
            words.append(effect.condition)
        if effect.pick is not None and effect.pick.ends_conditions:
            words.append(f"ends {' or '.join(effect.pick.ends_conditions)}")
        self._action_result_label.setText(" · ".join(words))
        self._action_result_label.setToolTip("")

    def _show_custom_condition_dialog(self, pick: str = ""):
        """Set up an effect on every target (see _apply_custom_effect): what
        it costs the source, a saving throw or an attack roll, damage, and a
        condition with its duration and a note. What the source can use is
        listed on the left, and a pick fills in the form. `pick` names a row
        to start with picked (a trigger's prompt: "Spirit Guardians:
        damage")."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return
        source = self.selected_character or self._current_turn_character()
        caster = self.selected_character
        targets = self.target_characters

        dlg = QDialog(self._window)
        dlg.setObjectName("customEffectDialog")
        dlg.setWindowTitle("Custom Effect")
        dlg.setStyleSheet(QSS)
        dlg.setMinimumWidth(_CUSTOM_DIALOG_WIDTH)
        dlg.resize(_effect_dialog_width(self._window), 0)
        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(10)

        # Who uses it on whom
        who_lbl = QLabel(_who_text(source, targets))
        who_lbl.setObjectName("effectWho")
        who_lbl.setTextFormat(Qt.TextFormat.RichText)
        who_lbl.setWordWrap(True)
        who_lbl.setToolTip(
            "Left-click a card for the source and right-click for targets"
            " before opening this."
        )
        outer.addWidget(who_lbl)

        body = QHBoxLayout()
        body.setSpacing(14)
        outer.addLayout(body, stretch=1)

        # What the source can use, on the left: a pick fills in the form, and
        # its rules text shows under the list.
        search_box, tree, category_items = self._effect_picker(source)
        details = QTextBrowser()
        details.setObjectName("effectDetails")
        details.setOpenLinks(False)
        details.setMinimumHeight(_DETAILS_MIN_HEIGHT)
        picker_box = QWidget()
        picker_box.setFixedWidth(_PICKER_WIDTH)
        picker = QVBoxLayout(picker_box)
        picker.setContentsMargins(0, 0, 0, 0)
        picker.setSpacing(6)
        picker.addWidget(search_box)
        picker.addWidget(tree, stretch=3)
        picker.addWidget(details, stretch=2)
        body.addWidget(picker_box)

        form = QVBoxLayout()
        form.setSpacing(8)
        body.addLayout(form, stretch=1)

        name_input = QLineEdit()
        name_input.setObjectName("effectName")
        name_input.setPlaceholderText("Name for the log (optional), e.g. Fireball")
        form.addWidget(name_input)

        # What to check about a pick, and what a monster's action does besides.
        note_lbl = QLabel("")
        note_lbl.setObjectName("effectNote")
        note_lbl.setWordWrap(True)
        note_lbl.hide()
        form.addWidget(note_lbl)

        columns = QHBoxLayout()
        columns.setSpacing(10)
        # The columns keep their widths whatever they show, so switching
        # between a saving throw and an attack roll doesn't move anything.
        column_widgets = []
        for stretch in (6, 5):
            column = QWidget()
            column.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
            )
            column_layout = QVBoxLayout(column)
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_layout.setSpacing(8)
            columns.addWidget(column, stretch=stretch)
            column_widgets.append(column_layout)
        roll_col, effect_col = column_widgets
        form.addLayout(columns, stretch=1)

        # ── Roll: none, a saving throw or an attack roll, and what it decides
        roll_frame, roll_box, _ = section("Roll")
        roll_col.addWidget(roll_frame)
        # The roll's value is two combo boxes, hidden behind the chips: an
        # attack, or a saving throw with an ability, or None for no roll.
        roll_combo = QComboBox()
        roll_combo.setObjectName("rollKind")
        roll_combo.addItems((SAVING_THROW, ATTACK_ROLL))
        roll_combo.setCurrentText(self._custom_save["roll"])
        roll_combo.hide()
        roll_box.addWidget(roll_combo)
        ability_combo = QComboBox()
        ability_combo.setObjectName("saveAbility")
        ability_combo.addItem("No saving throw", None)
        for full, short in ABILITIES:
            ability_combo.addItem(full, short)
        ability_combo.setCurrentIndex(
            max(ability_combo.findData(self._custom_save["ability"]), 0)
        )
        roll_box.addWidget(ability_combo)

        kind_row, kind_layout = row_widget("rollKindButtons")
        kind_layout.setSpacing(3)
        kind_buttons = {
            NO_ROLL: chip("&No roll", "Damage and the condition for everyone (Alt+N)"),
            SAVING_THROW: chip("&Saving throw", "Each target saves (Alt+S)"),
            ATTACK_ROLL: chip(
                "&Attack roll", "The source rolls against each target's AC (Alt+A)"
            ),
        }
        for button in kind_buttons.values():
            button.setProperty("rollKind", True)
            kind_layout.addWidget(button, stretch=1)
        roll_box.addWidget(kind_row)

        save_line, save_layout = row_widget()
        save_layout.setSpacing(8)
        ability_chips = chip_row(
            ability_combo,
            [(i, short, full) for i, (full, short) in enumerate(ABILITIES, start=1)],
            "saveAbilityButtons",
        )
        save_layout.addWidget(ability_chips, stretch=1)
        dc_label = QLabel("DC")
        save_layout.addWidget(dc_label)
        dc_input = QSpinBox()
        dc_input.setObjectName("saveDc")
        dc_input.setRange(1, MAX_SAVE_DC)
        same_source = self._custom_save["source"] is source
        known_dc = None if same_source else known_save_dc(source)
        dc_input.setValue(known_dc or self._custom_save["dc"])
        save_layout.addWidget(dc_input)
        roll_box.addWidget(save_line)

        attack_line, attack_layout = row_widget()
        bonus_label = QLabel("Attack bonus")
        attack_layout.addWidget(bonus_label)
        bonus_input = QSpinBox()
        bonus_input.setObjectName("attackBonus")
        bonus_input.setRange(MIN_ATTACK_BONUS, MAX_ATTACK_BONUS)
        bonus_input.setToolTip("What the source adds to its d20")
        known_bonus = None if same_source else known_attack_bonus(source)
        bonus_input.setValue(
            self._custom_save["bonus"] if known_bonus is None else known_bonus
        )
        attack_layout.addWidget(bonus_input)
        attack_layout.addStretch()
        roll_box.addWidget(attack_line)

        mode_combo = QComboBox()
        mode_combo.setObjectName("saveMode")
        mode_combo.addItems(ROLL_MODES)
        roll_box.addWidget(mode_combo)
        mode_chips = chip_row(
            mode_combo,
            [
                (0, "Neutral", "One d20"),
                (1, "Advantage", "Two d20s, the higher counts, for every target"),
                (2, "Disadvantage", "Two d20s, the lower counts, for every target"),
            ],
            "saveModeButtons",
        )
        roll_box.addWidget(mode_chips)

        half_box = QCheckBox("Half damage on a save")
        half_box.setObjectName("halfOnSave")
        half_box.setChecked(self._custom_save["half"])
        roll_box.addWidget(half_box)

        repeat_box = QCheckBox("Repeat the save at the end of each turn")
        repeat_box.setObjectName("repeatSave")
        repeat_box.setToolTip(
            "A save ends the condition. Monsters roll by themselves; players"
            " get a reminder."
        )
        roll_box.addWidget(repeat_box)

        resisters = [t for t in targets if legendary_resistances_left(t) > 0]
        resist_box = QCheckBox("Use Legendary Resistance on a failed save")
        resist_box.setObjectName("useLegendaryResistance")
        resist_box.setToolTip(
            "Left: "
            + ", ".join(
                f"{t['name']} {legendary_resistances_left(t)}" for t in resisters
            )
        )
        can_resist = bool(resisters)
        roll_box.addWidget(resist_box)

        # A roll made at the table is typed in; the rest are rolled. Each target
        # rolls a save for itself, and the source an attack against each one.
        rolls_hint = QLabel("Rolled at the table? Type it; blank rolls.")
        rolls_hint.setObjectName("secondary")
        roll_box.addWidget(rolls_hint)
        save_rows, typed_inputs, save_infos, _ = target_roll_rows(
            targets,
            "typedTotal",
            "The total with the save bonus already in it, like 14 or 9+5."
            " Blank rolls for them.",
        )
        roll_box.addWidget(save_rows)
        # A hit's extra damage (Hunter's Mark) is a roll of its own: a box
        # more on its target's row, for what was rolled at the table.
        extra_boxes = {
            id(target): [
                (
                    (id(target), label),
                    f"{label[len(source['name']) + 3:]}: {extra_text(extra)}",
                    f"{label}: what was rolled at the table for its"
                    f" {extra_text(extra)}, its dice twice over on a Critical"
                    " Hit. Blank rolls it, unless the damage is a total typed"
                    " in, which has it already. 0 leaves it out.",
                )
                for label, extra in hit_extras(source, target)
            ]
            for target in targets
            if source is not None
        }
        attack_rows, attack_inputs, attack_infos, extra_rows = target_roll_rows(
            targets,
            "typedAttack",
            "The total with the bonus already in it, like 17 or 12+5, or"
            " nat 20 or nat 1. Blank rolls for the source.",
            extra_boxes,
        )
        roll_box.addWidget(attack_rows)
        for target in targets:
            info = attack_infos[id(target)]
            info.setText(_attack_text(source, target))
            info.setToolTip(_attack_tooltip(source, target))
        roll_col.addStretch()

        # ── Damage, or Hit Points regained, or Temporary Hit Points
        damage_frame, damage_box, amount_header = section("Damage")
        effect_col.addWidget(damage_frame)
        amount_combo = QComboBox()
        amount_combo.setObjectName("amountKind")
        amount_combo.addItems(AMOUNT_KINDS)
        damage_box.addWidget(amount_combo)
        amount_chips = chip_row(
            amount_combo,
            [
                (0, DAMAGE_AMOUNT, "Each target it lands on takes it"),
                (1, HEALING, "Every target regains it, whatever the roll"),
                (2, TEMP_HP, "Every target gains it, whatever the roll"),
            ],
            "amountKindButtons",
        )
        damage_box.addWidget(amount_chips)
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
        damage_box.addLayout(damage_row)

        resistances_box = QCheckBox("Count resistances and immunities")
        resistances_box.setObjectName("countResistances")
        resistances_box.setChecked(True)
        damage_box.addWidget(resistances_box)
        times_line, times_layout = row_widget()
        times_layout.addWidget(QLabel("Times"))
        times_input = QSpinBox()
        times_input.setObjectName("effectTimes")
        times_input.setRange(1, MAX_EFFECT_TIMES)
        times_input.setToolTip(
            "Repeat it against each target, each time with its own attack roll,"
            " save and damage roll (Scorching Ray's rays, Eldritch Blast's"
            " beams). It costs the source once."
        )
        times_layout.addWidget(times_input)
        times_layout.addStretch()
        damage_box.addWidget(times_line)

        def amount_kind() -> str:
            return amount_combo.currentText()

        def show_amount_controls():
            """The box's title, hint and the damage-only controls, for what
            the amount is."""
            kind = amount_kind()
            is_damage = kind == DAMAGE_AMOUNT
            amount_header.setText(_AMOUNT_TITLES[kind])
            damage_input.setPlaceholderText(_AMOUNT_HINTS[kind])
            damage_input.setToolTip(
                "Dice are rolled once, for everyone it hits"
                if is_damage
                else "Dice are rolled once, for every target"
            )
            for widget in (type_combo, resistances_box):
                widget.setVisible(is_damage)

        # ── Condition
        condition_frame, condition_box, condition_header = section("Condition")
        effect_col.addWidget(condition_frame)
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
        condition_box.addWidget(name_combo)

        notes_input = QLineEdit()
        notes_input.setObjectName("conditionNotes")
        notes_input.setPlaceholderText("Notes (optional, shown on hover)")
        condition_box.addWidget(notes_input)

        duration_combo = QComboBox()
        duration_combo.setObjectName("conditionDuration")
        duration_combo.setToolTip("How long the condition lasts")
        for label, duration in CUSTOM_CONDITION_DURATIONS:
            if duration is not None and duration.get("of") == "source":
                if source is None:
                    continue
                label = label.format(source=source["name"])
            duration_combo.addItem(label, duration)
        duration_combo.addItem("Custom...", "custom")
        condition_box.addWidget(duration_combo)

        custom_row = QHBoxLayout()
        amount_input = QSpinBox()
        amount_input.setObjectName("durationAmount")
        amount_input.setRange(1, MAX_DURATION_AMOUNT)
        custom_row.addWidget(amount_input)
        unit_combo = QComboBox()
        unit_combo.setObjectName("durationUnit")
        unit_combo.addItems(list(CUSTOM_DURATION_UNITS))
        custom_row.addWidget(unit_combo, stretch=1)
        custom_widgets = (amount_input, unit_combo)
        condition_box.addLayout(custom_row)

        # ── What it costs the source
        cost_title = f"Cost to {caster['name']}" if caster is not None else "Cost"
        cost_frame, cost_box, _ = section(cost_title)
        effect_col.addWidget(cost_frame)
        slot_combo = QComboBox()
        slot_combo.setObjectName("spellSlot")
        slot_combo.addItem("No spell slot", None)
        for label, level in spell_slot_choices(caster or {}, 1):
            if level is not None:
                slot_combo.addItem(label, level)
        cost_box.addWidget(slot_combo)
        # How many creatures the pick may target (Bless: 3), at the slot chosen.
        target_count_lbl = QLabel("")
        target_count_lbl.setObjectName("targetCount")
        target_count_lbl.setWordWrap(True)
        target_count_lbl.hide()
        cost_box.addWidget(target_count_lbl)
        action_combo = QComboBox()
        action_combo.setObjectName("actionCost")
        action_combo.addItem("No action", None)
        for action_type in self.ACTION_ECONOMY_TYPES:
            action_combo.addItem(action_type, action_type)
        cost_box.addWidget(action_combo)
        action_chips = chip_row(
            action_combo,
            [(0, "None", "Spends no action")]
            + [
                (i, action_type, f"Spends the source's {action_type}")
                for i, action_type in enumerate(self.ACTION_ECONOMY_TYPES, start=1)
            ],
            "actionCostButtons",
        )
        cost_box.addWidget(action_chips)
        concentrate_box = QCheckBox("Source concentrates on it")
        concentrate_box.setObjectName("sourceConcentrates")
        concentrate_box.setToolTip(
            "Starts Concentrating, ending any other concentration. When it"
            " ends, the condition comes off the targets."
        )
        cost_box.addWidget(concentrate_box)
        for widget in (slot_combo, action_combo, concentrate_box):
            widget.setEnabled(caster is not None)
        if caster is None:
            no_cost = QLabel("No source picked: left-click a card to spend from it.")
            no_cost.setObjectName("secondary")
            no_cost.setWordWrap(True)
            cost_box.addWidget(no_cost)
        effect_col.addStretch()

        # ── What Apply will do, what's wrong, and the buttons
        preview_lbl = QLabel("")
        preview_lbl.setObjectName("effectPreview")
        preview_lbl.setWordWrap(True)
        outer.addWidget(preview_lbl)

        btn_row = QHBoxLayout()
        footer = QVBoxLayout()
        footer.setSpacing(2)
        problem_lbl = QLabel("")
        problem_lbl.setObjectName("statusLabel")
        problem_lbl.setWordWrap(True)
        footer.addWidget(problem_lbl)
        keys_lbl = QLabel(
            "↑↓ browse · Enter picks, again applies · Ctrl+Enter apply"
            " · Alt+N/S/A roll · Ctrl+F search"
        )
        keys_lbl.setObjectName("secondary")
        footer.addWidget(keys_lbl)
        btn_row.addLayout(footer, stretch=1)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setAutoDefault(False)
        cancel_btn.setMinimumWidth(_BUTTON_WIDTH)
        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.setAutoDefault(False)
        apply_btn.setMinimumWidth(_BUTTON_WIDTH)
        apply_btn.setToolTip(f"Apply to {_count(len(targets), 'target')} (Ctrl+Enter)")
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(apply_btn)
        outer.addLayout(btn_row)

        # The ability a saving throw goes back to after "No roll".
        last_ability = {"value": ability_combo.currentData() or "DEX"}

        def roll_kind() -> str:
            if roll_combo.currentText() == ATTACK_ROLL:
                return ATTACK_ROLL
            return SAVING_THROW if ability_combo.currentData() is not None else NO_ROLL

        def choose_kind(kind: str):
            roll_combo.setCurrentText(
                ATTACK_ROLL if kind == ATTACK_ROLL else SAVING_THROW
            )
            if kind == NO_ROLL:
                ability_combo.setCurrentIndex(0)
            elif kind == SAVING_THROW and ability_combo.currentData() is None:
                ability_combo.setCurrentIndex(
                    max(ability_combo.findData(last_ability["value"]), 1)
                )
            show_roll_controls()

        for kind, button in kind_buttons.items():
            button.clicked.connect(lambda _=False, k=kind: choose_kind(k))

        def show_custom_row():
            for widget in custom_widgets:
                widget.setVisible(duration_combo.currentData() == "custom")

        def show_save_bonuses():
            ability = ability_combo.currentData()
            if ability is not None:
                last_ability["value"] = ability
            for target in targets:
                info = save_infos[id(target)]
                if ability is None:
                    info.setText("")
                    continue
                info.setText(_save_text(target, ability))
                info.setToolTip(_save_tooltip(target, ability))

        def show_roll_controls():
            kind = roll_kind()
            is_attack = kind == ATTACK_ROLL
            has_save = kind == SAVING_THROW
            for name, button in kind_buttons.items():
                button.setChecked(name == kind)
            save_line.setVisible(not is_attack)
            for widget in (dc_label, dc_input):
                widget.setVisible(has_save)
            attack_line.setVisible(is_attack)
            mode_chips.setVisible(kind != NO_ROLL)
            repeat_box.setVisible(has_save)
            # Hit Points aren't halved by a save: every target gets them.
            half_box.setVisible(has_save and amount_kind() == DAMAGE_AMOUNT)
            resist_box.setVisible(can_resist and has_save)
            rolls_hint.setVisible(kind != NO_ROLL)
            save_rows.setVisible(bool(typed_inputs) and has_save)
            attack_rows.setVisible(bool(attack_inputs) and is_attack)
            for row in extra_rows.values():
                for widget in row:
                    widget.setVisible(amount_kind() == DAMAGE_AMOUNT)
            mode_combo.setEnabled(has_save or is_attack)
            for widget in (dc_input, half_box, repeat_box, resist_box):
                widget.setEnabled(has_save)
            for total_input in typed_inputs.values():
                total_input.setEnabled(has_save)
            condition_header.setText(
                {
                    ATTACK_ROLL: "Condition (on a hit)",
                    SAVING_THROW: "Condition (on a failed save)",
                }.get(kind, "Condition")
            )
            show_save_bonuses()

        def show_typed_type(text: str):
            if amount_kind() != DAMAGE_AMOUNT:
                return  # healing has no type
            try:
                parts = rolled_damage(_DICELESS.sub("1", text))
            except AmountError:
                return
            if parts[0][1] is not None:
                type_combo.setCurrentIndex(type_combo.findData(parts[0][1]))

        def show_preview():
            """What Apply will do, in a line, so a wrong pick shows before it
            lands. Nothing here is rolled."""
            kind = roll_kind()
            mode = mode_combo.currentText()
            with_mode = f" with {mode}" if kind != NO_ROLL and mode != "Neutral" else ""
            parts = []
            if kind == SAVING_THROW:
                parts.append(
                    f"DC {dc_input.value()} {ability_combo.currentText()} save{with_mode}"
                )
            elif kind == ATTACK_ROLL:
                parts.append(f"Attack {bonus_input.value():+d} vs AC{with_mode}")
            amount = amount_kind()
            if amount == DAMAGE_AMOUNT:
                damage = _damage_preview(damage_input.text(), type_combo.currentData())
                if damage and kind == SAVING_THROW:
                    damage += (
                        ", half on a save"
                        if half_box.isChecked()
                        else ", none on a save"
                    )
                if damage:
                    parts.append(damage)
            elif damage_input.text().strip():
                parts.append(
                    _amount_text(damage_input.text().strip(), amount) + " for all"
                )
            condition = name_combo.currentText().strip()
            if condition:
                lasts = duration_combo.currentText()
                if duration_combo.currentData() == "custom":
                    lasts = f"{amount_input.value()} {unit_combo.currentText()}"
                if duration_combo.currentData() is not None:
                    condition += f" ({lasts[0].lower()}{lasts[1:]})"
                if kind == SAVING_THROW and repeat_box.isChecked():
                    condition += ", save ends"
                parts.append(condition)
            costs = []
            if caster is not None:
                if slot_combo.currentData() is not None:
                    costs.append(slot_combo.currentText())
                if action_combo.currentData() is not None:
                    costs.append(action_combo.currentText())
                if concentrate_box.isChecked():
                    costs.append("concentration")
            if costs:
                parts.append("costs " + ", ".join(costs))
            if not parts:
                preview_lbl.setText(
                    "Pick something on the left, or fill in a roll, damage,"
                    " healing or a condition."
                )
                return
            preview_lbl.setText(
                f"On {_count(len(targets), 'target')}: " + " · ".join(parts)
            )

        duration_combo.currentIndexChanged.connect(show_custom_row)
        roll_combo.currentIndexChanged.connect(show_roll_controls)
        ability_combo.currentIndexChanged.connect(show_roll_controls)
        amount_combo.currentIndexChanged.connect(show_amount_controls)
        amount_combo.currentIndexChanged.connect(show_roll_controls)
        damage_input.textChanged.connect(show_typed_type)
        for signal in (
            amount_combo.currentIndexChanged,
            roll_combo.currentIndexChanged,
            ability_combo.currentIndexChanged,
            mode_combo.currentIndexChanged,
            dc_input.valueChanged,
            bonus_input.valueChanged,
            half_box.toggled,
            repeat_box.toggled,
            damage_input.textChanged,
            type_combo.currentIndexChanged,
            name_combo.currentTextChanged,
            duration_combo.currentIndexChanged,
            amount_input.valueChanged,
            unit_combo.currentIndexChanged,
            slot_combo.currentIndexChanged,
            action_combo.currentIndexChanged,
            concentrate_box.toggled,
        ):
            signal.connect(show_preview)
        show_custom_row()
        show_amount_controls()
        show_roll_controls()
        show_preview()

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

        def typed_extras() -> dict[int, dict[str, int]] | None:
            """The extra damage rolled at the table, by target and what gives
            it, or None having said what's wrong with one."""
            extras: dict[int, dict[str, int]] = {}
            for (key, label), (_, extra_input) in extra_rows.items():
                text = extra_input.text().strip()
                if not text:
                    continue
                total = int(text) if _WHOLE_NUMBER.fullmatch(text) else None
                if total is None:
                    total = parse_amount(text)
                if total is None or total < 0:
                    problem_lbl.setText(
                        f"'{text}' isn't an amount of damage for {label}."
                    )
                    return None
                extras.setdefault(key, {})[label] = total
            return extras

        def do_apply():
            if applied:
                return
            is_attack = roll_combo.currentText() == ATTACK_ROLL
            ability = None if is_attack else ability_combo.currentData()
            # "stunned" is Stunned, so the rules see it as they should; and
            # "Frightened + Incapacitated" is both.
            condition = CONDITION_JOINER.join(
                next((s for s in suggestions if s.lower() == typed.lower()), typed)
                for typed in condition_names(name_combo.currentText())
            )
            kind = amount_kind()
            damage: list[tuple[int, str]] = []
            hit_points = 0
            if kind == DAMAGE_AMOUNT:
                damage, problem = read_damage(
                    damage_input.text(), type_combo.currentData()
                )
            else:
                hit_points, problem = read_hit_points(damage_input.text(), kind)
            if problem:
                problem_lbl.setText(problem)
                return
            pick: EffectOption | None = picked["option"]
            # A pick the source spends (a feature with no numbers) is enough.
            spends = pick is not None and pick.is_tracked and caster is not None
            ends = pick is not None and bool(pick.ends_conditions)
            if (
                not is_attack
                and ability is None
                and not damage
                and not hit_points
                and not condition
                and not spends
                and not ends
            ):
                problem_lbl.setText(
                    "Add a saving throw, damage, healing or a condition."
                )
                return
            totals = typed_totals() if ability is not None else {}
            attacks = typed_attacks() if is_attack else {}
            extras = typed_extras() if is_attack and kind == DAMAGE_AMOUNT else {}
            if totals is None or attacks is None or extras is None:
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
            if is_attack and kind == DAMAGE_AMOUNT:
                critical_damage, _ = read_damage(
                    damage_input.text(), type_combo.currentData(), critical=True
                )
            effect = CustomEffect(
                name=name_input.text().strip(),
                condition=condition,
                duration=duration,
                notes=notes_input.text(),
                damage=damage,
                critical_damage=critical_damage,
                count_resistances=resistances_box.isChecked(),
                healing=hit_points if kind == HEALING else 0,
                temp_hp=hit_points if kind == TEMP_HP else 0,
                slot_level=slot_combo.currentData(),
                action_cost=action_combo.currentData(),
                concentration=concentrate_box.isChecked(),
                attack_bonus=bonus_input.value() if is_attack else None,
                typed_attacks=attacks,
                typed_extras=extras,
                ability=ability,
                dc=dc_input.value(),
                mode=mode_combo.currentText(),
                half_on_save=half_box.isChecked(),
                use_legendary_resistance=resist_box.isChecked(),
                repeat_save=repeat_box.isChecked(),
                typed_totals=totals,
                pick=pick,
                weapon_attack=pick.weapon_attack if pick is not None else None,
                # A total with no dice, not the pick's own damage, was rolled
                # at the table: a hit's extra damage isn't added to it.
                typed_damage=bool(damage)
                and not _DICELESS.search(damage_input.text())
                and damage_input.text() != picked["damage"],
            )
            times = times_input.value()
            if times == 1:
                self._apply_custom_effect(effect)
            else:
                self._apply_custom_effects(repeated(effect, times))
            dlg.accept()

        def repeated(effect: CustomEffect, times: int) -> list[CustomEffect]:
            """`effect` `times` over: each with its own damage roll, named
            "Scorching Ray (2 of 3)" in the log, and only the first costing
            the source anything or using the totals typed in."""
            kind = amount_kind()
            effects = []
            for index in range(times):
                each = replace(effect, name=f"{effect.name} ({index + 1} of {times})")
                if index:
                    damage: list[tuple[int, str]] = []
                    critical: list[tuple[int, str]] = []
                    hit_points = 0
                    if kind == DAMAGE_AMOUNT:
                        damage, _ = read_damage(
                            damage_input.text(), type_combo.currentData()
                        )
                        if effect.attack_bonus is not None:
                            critical, _ = read_damage(
                                damage_input.text(),
                                type_combo.currentData(),
                                critical=True,
                            )
                    else:
                        hit_points, _ = read_hit_points(damage_input.text(), kind)
                    each = replace(
                        each,
                        damage=damage,
                        critical_damage=critical,
                        healing=hit_points if kind == HEALING else 0,
                        temp_hp=hit_points if kind == TEMP_HP else 0,
                        slot_level=None,
                        action_cost=None,
                        concentration=False,
                        typed_attacks={},
                        typed_totals={},
                        typed_extras={},
                        pick=None,
                        row=effect.pick.name if effect.pick is not None else "",
                    )
                effects.append(each)
            return effects

        # The pick, and the damage and search it was made with, to tell the
        # GM's edits by.
        picked: dict = {"option": None, "damage": "", "times": 1, "search": ""}

        def show_details(option: EffectOption | None):
            details.setHtml(
                _option_details(option) if option is not None else _DETAILS_HINT
            )

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
            amount_combo.setCurrentText(option.amount_kind)
            damage = option.damage_at(slot_combo.currentData())
            damage_input.setText(damage)
            times = option.instances_at(slot_combo.currentData())
            times_input.setValue(times)
            name_combo.setCurrentText(option.condition)
            notes_input.clear()
            show_duration(option.duration_seconds, option.until)
            problem_lbl.setText("")
            show_details(option)
            show_target_count(option)
            picked.update(
                option=option, damage=damage, times=times, search=search_box.text()
            )

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
            show_details(None)
            show_target_count(None)

        def show_target_count(option: EffectOption | None):
            """How many creatures the pick may target at the slot chosen
            ("Targets: 4 at level 2" for Bless), and when more are targeted,
            how many too many. It warns; the GM can still apply it."""
            slot = slot_combo.currentData()
            count = option.targets_at(slot) if option is not None else None
            if option is None or count is None:
                target_count_lbl.hide()
                return
            at = f" at level {int(slot)}" if option.target_upcast and slot else ""
            text = f"Targets: {count}{at}"
            if len(targets) > count:
                text += f" ({len(targets)} targeted: {len(targets) - count} too many)"
            target_count_lbl.setText(text)
            target_count_lbl.show()

        def upcast():
            """A pick's damage and times at the slot now chosen, unless they've
            been edited."""
            option = picked["option"]
            show_target_count(option)
            if option is None:
                return
            if times_input.value() == picked["times"]:
                picked["times"] = option.instances_at(slot_combo.currentData())
                times_input.setValue(picked["times"])
            if damage_input.text() != picked["damage"]:
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

        def on_current_changed(item: QTreeWidgetItem | None):
            """A greyed row can't be picked, but its rules text can be read."""
            if item is not None and item.isDisabled():
                show_details(item.data(0, Qt.ItemDataRole.UserRole))

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

        def focus_search():
            search_box.setFocus()
            search_box.selectAll()

        # Up and Down from the search box pick as they go (fill_from), so
        # Enter applies the row they reached.
        SearchKeys(search_box, tree)
        tree.itemSelectionChanged.connect(on_selection_changed)
        tree.currentItemChanged.connect(on_current_changed)
        tree.itemActivated.connect(item_activated)
        search_box.returnPressed.connect(search_entered)
        slot_combo.currentIndexChanged.connect(upcast)
        name_input.textEdited.connect(drop_pick)

        apply_btn.clicked.connect(do_apply)
        name_edit.returnPressed.connect(do_apply)
        notes_input.returnPressed.connect(do_apply)
        damage_input.returnPressed.connect(do_apply)
        name_input.returnPressed.connect(do_apply)
        for total_input in [
            *typed_inputs.values(),
            *attack_inputs.values(),
            *(box for _, box in extra_rows.values()),
        ]:
            total_input.returnPressed.connect(do_apply)
        cancel_btn.clicked.connect(dlg.reject)
        for keys, action in (
            ("Ctrl+Return", do_apply),
            ("Ctrl+Enter", do_apply),
            ("Ctrl+F", focus_search),
        ):
            QShortcut(QKeySequence(keys), dlg).activated.connect(action)

        show_details(None)
        search_box.setFocus()
        start = next(
            (
                category.child(i)
                for category in category_items.values()
                for i in range(category.childCount())
                if (option := option_of(category.child(i))) is not None
                and option.name == pick
            ),
            None,
        )
        if pick and start is not None:
            tree.setCurrentItem(start)
            tree.scrollToItem(start)
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
    def _add_action_use(
        self, action_type: str, char: dict | None = None, *, ask: bool = True
    ):
        """Log a use of Action/Bonus Action/Reaction for char (the source if
        None), this round. Tallies reset when it becomes that combatant's turn
        again (see _advance_turn). When char has used it already this round,
        the GM is asked whether to log it anyway, unless the caller asked
        already, along with the rest of what it costs (ask=False).
        """
        if self.phase == "PARTY":
            return  # between encounters there are no turns to spend them in
        char = char or self.selected_character
        if not char:
            self._show_status("Nothing logged: left-click a card to pick a source.")
            return
        if ask and not self._go_ahead_anyway(
            char,
            f"Log another {action_type}",
            [self._action_lack(char, action_type)],
        ):
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
