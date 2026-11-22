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
    QGridLayout,
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

from Combat.Arena.arena import (
    DASHES_KEY,
    GRAPPLER_KEY,
    MOVED_KEY,
    dashes,
    grappled_by,
    movement_ft,
    movements,
    position,
    remaining_ft,
    stand_up_ft,
    walking_speed_ft,
)
from Combat.Arena.ranges import (
    NO_RANGE_CHECK,
    RangeCheck,
    spell_range_warning,
)
from Combat.Arena.lasting import AREA_KEY, find_area, record_origin
from Combat.Definitions import (
    Action,
    ActionCost,
    CombatStatus,
    ConditionRule,
    Phase,
)
from Combat.Effects.active_effects import (
    CUSTOM,
    FEATURE,
    SPELL,
    ActiveEffect,
    active_effects,
    describe,
    drop_repeat_save,
    duration_entry,
    find_effect,
    give_modifiers,
    is_linked,
    link_badge,
    link_concentration,
    linked_badges_left_without,
    linked_conditions,
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
    has_condition,
    hit_extras,
    hit_plan,
    hit_point_maximum,
    hit_point_maximum_notes,
    loses_dodge,
    rolled_modifiers,
    rules_condition,
    signed,
)
from Model.Content.CombatModifiers import Modifier
from Combat.Effects.triggers import (
    AttackOutcome,
    FailedSaveOutcome,
    OpportunityAttack,
    UsesOutcome,
    outcome_firings,
    reduced_damage,
)
from Combat.WildShape import current_form, form_badge
from Core.Definitions import Condition, DamageType
from Core.Rules import SECONDS_PER_ROUND
from Model.Content.CombatModifiers import AttackKind, HitPointMaximum
from Model.Content.RulesConditions import conditions_with
from Model.Content.StandardActions import DASH, DODGE, HIDDEN
from .amounts import AmountError, parse_amount
from .attack_rolls import (
    AttackRoll,
    armor_bonus,
    armor_in_use,
    cover_bonus,
    has_shield,
    is_shield_off,
    parse_attack_roll,
    stored_armor,
    SHIELD_OFF,
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
    pick_attack_range,
    pick_spell_range_ft,
    regained_uses,
    spell_slot_choices,
    triggered_rows,
)
from .features_mixin import FEATURE_BADGE_COLOR
from .monster_actions import legendary_resistances_left, roll_dice
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
    STANDARD_ACTION,
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
from .tree_filter import filter_category_tree, first_visible_item
from .undo import undoable
from .use_cast import form as use_cast_form
from .use_cast.form import read_or_say

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


def _option_duration(option: EffectOption) -> dict | None:
    """How long what a picked row gives lasts, as a CustomEffect says it."""
    if option.until is not None:
        return {"until": option.until[0], "of": option.until[1]}
    if option.duration_seconds:
        return {"seconds": option.duration_seconds}
    return None


def hit_rider(option: EffectOption) -> CustomEffect | None:
    """What a hit with `option` gives the target beside its damage (Molten
    Strike's Prone), as the Custom Effect dialog would, with no damage of its
    own: for a monster's action button, whose damage goes through the Damage
    field (DI-082). None when the row gives nothing."""
    if not option.condition:
        return None
    return CustomEffect(
        name=option.name,
        condition=option.condition,
        duration=_option_duration(option),
        pick=option,
    )


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
    duration = _option_duration(option)
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
        push=option.push,
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
# Room above the dialog's first minimum height, for what a pick shows (a note,
# extra rows: up to ~95px more). Opened at its bare minimum, the dialog had to
# grow while shown, and Windows printed "QWindowsWindow::setGeometry: Unable
# to set geometry".
_DIALOG_HEADROOM = 120
_BUTTON_WIDTH = 110
# The dialog's target boxes: how many to a line, and their + and × buttons.
_TARGETS_PER_LINE = 4
_TARGET_BUTTON_WIDTH = 28
_NO_TARGET = "— Pick a target —"
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


def _source_text(source: dict | None) -> str:
    """The Custom Effect dialog's first line, before its target boxes: the
    source and an arrow to them."""
    if source is None:
        return "<span style='color:#a0a0b0'>No source</span> →"
    who = escape(source["name"], quote=False)
    return f"<span style='color:#c9a84c'>{who}</span> →"


def _with_shield(target: dict, wielding: bool | None) -> dict:
    """Target as it is with its Shield wielded or set down (`wielding`, the
    Custom Effect dialog's Shield box), to work its AC out by; target itself
    for None, or one without a Shield."""
    if wielding is None or not has_shield(target):
        return target
    return {**target, SHIELD_OFF: not wielding}


def _ignores_cover(pick: EffectOption | None) -> bool:
    """Whether a pick takes Half and Three-Quarters Cover away
    (EffectOption.ignores_cover: Sacred Flame), so only the map's Total
    Cover is left."""
    return pick is not None and pick.ignores_cover


def _armor_text(target: dict, wielding: bool | None = None) -> str:
    """What an attack roll against target has to meet: "AC 15", with its
    cover in it ("AC 17 (cover)"), or "AC ?" when that isn't known.
    `wielding`: whether it wields its Shield, None as it is now."""
    target = _with_shield(target, wielding)
    armor = stored_armor(target)
    if armor is None:
        return "AC ?"
    armor += armor_bonus(target)
    return f"AC {armor} (cover)" if cover_bonus(target) else f"AC {armor}"


def _bonus_notes(plan: RollPlan) -> list[str]:
    """What adds to a roll, for a tooltip: "Bless: +1d4"."""
    return [f"{label}: {signed(amount)}" for label, amount in plan.bonuses]


def _attack_text(
    source: dict | None,
    target: dict,
    wielding: bool | None = None,
    distance_ft: int | None = None,
    covered: dict | None = None,
    reach: RangeCheck = NO_RANGE_CHECK,
) -> str:
    """A target's row for an attack roll: what it has to meet, the mode the
    modifiers give it and what they add to it, to roll it that way at the
    table ("AC 15, Advantage", "AC 15, +1d4 to hit"). The extra damage a hit
    on it deals has a row of its own under it (target_roll_rows' extras).
    `wielding`: whether it wields its Shield (_armor_text). `distance_ft`:
    how far the source is on the map, which settles Prone's "within 5
    feet" (attack_plan). `covered`: target with the map's cover from the
    source in it (_covered), whose AC it has to meet. `reach`: what the map
    says of its range (Long range's Disadvantage counted, past its reach
    warned about after the rest: "AC 15; past the 5 ft. reach")."""
    plan = attack_plan(
        source,
        target,
        "Neutral",
        distance_ft=distance_ft,
        extra=reach.modifiers,
        sight=reach.sight,
    )
    parts = [_armor_text(covered or target, wielding)]
    if plan.mode != "Neutral":
        parts.append(plan.mode)
    flat, dice = bonus_reminder(plan)
    added = " ".join(p for p in (f"{flat:+d}" if flat else "", dice) if p)
    if added:
        parts.append(f"{added} to hit")
    return "; ".join([", ".join(parts), *_short_warnings(reach)])


def _short_warnings(reach: RangeCheck) -> list[str]:
    """A range warning as a row says it, without the target's name and
    distance its row already shows: "past the 5 ft. reach"."""
    return [w.split(" away, ", 1)[-1] for w in reach.warnings]


def _attack_tooltip(
    source: dict | None,
    target: dict,
    distance_ft: int | None = None,
    cover_text: str = "",
    reach: RangeCheck = NO_RANGE_CHECK,
) -> str:
    """The attack row's tooltip: what changes the AC, with `cover_text`, the
    map's cover from the source ("Half Cover from Barrel at C4: +2 AC and
    DEX saves"), how it's rolled (`reach`: the map's range, counted) and
    what a hit adds."""
    plan = attack_plan(
        source,
        target,
        "Neutral",
        distance_ft=distance_ft,
        extra=reach.modifiers,
        sight=reach.sight,
    )
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
            *([cover_text] if cover_text else []),
            *armor_class_notes(target),
            *plan.notes,
            *reach.notes,
            *reach.warnings,
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


def _with_slot(record: dict, slot: int | None) -> dict:
    """A kept area's record with the slot level it was cast with, for its
    damage when it acts again (arena step 24); as it was without a slot."""
    if slot is None:
        return record
    return {**record, "slot_level": int(slot)}


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def _effect_dialog_width(window: QWidget | None) -> int:
    """The Custom Effect dialog's width on the window's screen."""
    screen = window.screen() if window is not None else None
    if screen is None:
        return _CUSTOM_DIALOG_WIDTH
    room = screen.availableGeometry().width() - _SCREEN_MARGIN
    return max(_CUSTOM_DIALOG_WIDTH, min(_PREFERRED_DIALOG_WIDTH, room))


def _effect_dialog_height(dialog: QWidget) -> int:
    """The Custom Effect dialog's height: its minimum plus room to grow into
    (_DIALOG_HEADROOM), as far as its screen allows."""
    minimum = dialog.minimumSizeHint().height()
    screen = dialog.screen()
    if screen is None:
        return minimum + _DIALOG_HEADROOM
    room = screen.availableGeometry().height() - _SCREEN_MARGIN
    return max(minimum, min(minimum + _DIALOG_HEADROOM, room))


class ConditionsMixin(CombatWindowState):
    """Mixin for condition and visibility management."""

    @undoable
    def _add_condition_to(
        self,
        char: dict,
        cond: str,
        source: dict | None = None,
        *,
        counted: bool = True,
    ):
        """char gets `cond` from `source`, logged. Not `counted` in the fight's
        stats: a spell's badge beside the conditions it gave (Friends beside
        Charmed), which aren't one more condition."""
        if cond == DASH:
            # Each Dash this turn is its Speed again on the map, a second
            # one (Cunning Action's) too, which the badge it has can't say.
            self._take_dash(char)
        if (
            cond == Condition.GRAPPLED.value
            and source is not None
            and source is not char
        ):
            # Who grapples it: the battle map drags it along (arena step 22).
            char[GRAPPLER_KEY] = source["name"]
        if cond not in char["conditions"]:
            char["conditions"].append(cond)
            char.setdefault("stats", _default_stats())
            if counted:
                char["stats"]["conditions_received"] = (
                    char["stats"].get("conditions_received", 0) + 1
                )
                increment_named_stat(char["stats"], "conditions_received_by_name", cond)
            source_name = source["name"] if source is not None else None
            if source is not None and counted:
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
            if not counted:
                # So replaying it doesn't count it either (stats.py's
                # is_counted_condition).
                cond_value["counted"] = False
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
            # And its grapples (Rules Glossary, Grappling: "The condition also
            # ends if the grappler has the Incapacitated condition").
            if incapacitates(cond):
                for held in grappled_by(char, self.characters):
                    self._remove_condition_from(
                        held, Condition.GRAPPLED.value, source=char
                    )
            # The Dodge action's benefits are lost to Incapacitated or a
            # Speed of 0 (Grappled); they don't count from then on anyway.
            if cond != DODGE and DODGE in char["conditions"] and loses_dodge(char):
                self._remove_condition_from(char, DODGE)

    def _take_dash(self, char: dict):
        """char takes the Dash action (or a feature's): as much movement
        again as its Speed, this turn, a GM-only log line."""
        char[DASHES_KEY] = dashes(char) + 1
        movement = movement_ft(char)
        if movement is not None:
            self._log_event(
                f"{char['name']} dashes: {movement} ft. of movement this turn",
                character=char["name"],
                public=False,
            )

    def _stand_up(self, char: dict):
        """char rights itself from Prone, as Prone is taken off it on its own
        turn while it's on the map: that spends its movement (stand_up_ft:
        half its Speed, 5 ft. with Athlete's Hop Up), counted as moved, a
        GM-only log line. Prone ending on another's turn (the GM correcting
        a mistake, a feature standing it up) or off the map spends nothing.
        A Speed of 0, or too little movement left, is warned about, not
        refused, as a move past its Speed is."""
        if position(char) is None or not any(
            char is c for c in self._current_turn_group()
        ):
            return
        cost = stand_up_ft(char)
        if cost is None:
            return
        name = char["name"]
        given = [s for s, m in movements(char) if m.stands_up_ft == cost]
        why = f" ({given[0]})" if given else ""
        left = remaining_ft(char)
        char[MOVED_KEY] = int(char.get(MOVED_KEY, 0)) + cost
        self._log_event(
            f"{name} stands up{why}: {cost} ft. of movement,"
            f" {remaining_ft(char)} ft. left this turn",
            character=name,
            public=False,
        )
        if walking_speed_ft(char) == 0:
            self._show_status(f"{name} has a Speed of 0 and can't stand up.")
        elif cost > left:
            self._show_status(
                f"{name} stands up with {left} ft. of movement left; it costs"
                f" {cost} ft."
            )

    def _give_badge_modifiers(
        self,
        char: dict,
        name: str,
        modifiers,
        *,
        levels_up: int = 0,
        source: dict | None = None,
        rolled_maximum: int | None = None,
    ):
        """char's badge `name` gives `modifiers` while it's on, their dice
        rolled now (rolled_modifiers), or a Hit Point maximum's as
        `rolled_maximum`, rolled at the table (upcast and all; 8.6). One that raises its Hit Point maximum
        raises its current Hit Points by as much (Aid: "Hit Point maximum and
        current Hit Points increase by 5"), as Hit Points regained from
        `source`, so a creature at 0 HP comes to; one that lowers it leaves
        no more than the new maximum."""
        before = hit_point_maximum(char)
        if rolled_maximum is not None:
            modifiers = [
                (
                    HitPointMaximum(str(rolled_maximum))
                    if isinstance(m, HitPointMaximum) and not m.rolled
                    else m
                )
                for m in modifiers
            ]
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
            stands_for = linked_conditions(char, cond)
            char["conditions"].remove(cond)
            # Its tooltip, colour, timer and repeat save go with it.
            remove_effect(char, cond)
            if cond == DASH:
                char.pop(DASHES_KEY, None)  # and the Dash's movement
            if cond == Condition.GRAPPLED.value:
                char.pop(GRAPPLER_KEY, None)  # and who grappled it
            emptied = linked_badges_left_without(char, cond)
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
            if cond == Condition.PRONE.value:
                self._stand_up(char)
            if (
                cond == Condition.UNCONSCIOUS.value
                and not has_condition(char, Condition.PRONE)
                and not is_immune_to(char, Condition.PRONE.value)
                and self._char_death_state(char) != "dead"
            ):
                # Unconscious: "When this condition ends, you remain Prone."
                # Its own Prone went with it (held_conditions), so the
                # creature is given one, logged, which standing up ends.
                self._add_condition_to(char, Condition.PRONE.value, counted=False)
            self._forget_effect_on(char, cond)
            # A spell's badge and the conditions it stands for go together
            # (Friends and Charmed): those no other badge stands for, and a
            # badge left standing for none. Not Unconscious from 0 HP.
            for other in [*stands_for, *emptied]:
                if (
                    other in char["conditions"]
                    and not is_linked(char, other)
                    and (other != Condition.UNCONSCIOUS.value or char["hp"] > 0)
                ):
                    self._remove_condition_from(char, other, source=source)
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
            # Its caster, unless it has one: re-adding Hanna's Hunter's Mark
            # by hand with the Pirate selected mustn't give the Pirate its
            # extra damage (DI-074).
            record = find_effect(target, cond)
            if record is None or not record.get("caster"):
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
        if not living and effect.area is None:
            self._show_status("Nothing applied: every target is dead.")
            return
        source = self.selected_character or self._current_turn_character()
        caster = self.selected_character
        label = effect.name or effect.condition or "the effect"
        logged_use = False
        # A kept area acting again (from_area) spends nothing: its cast did.
        if caster is not None and not effect.from_area:
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
        # Who its push moves: those its conditions land on (arena step 21).
        to_push = []
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
            if effect.pick is not None and effect.pick.regains:
                self._regain_feature_uses(target, effect.pick)
            drops_to = effect.pick.drops_to if effect.pick is not None else 0
            if drops_to and target["hp"] <= 0:
                # Picked late (asked too late, or the setting off): what it
                # would have dropped to instead of 0, it comes back up to.
                self._heal_target(target, drops_to, source)
            saved = any(target is s for s in self._saved_targets)
            damage = effect.damage
            hit: bool | None = None
            critical = False
            if effect.attack_bonus is not None:
                # Its Shield wielded or set down first, as the dialog said.
                self._set_shield(target, effect.shields.get(id(target)))
                # The attacker's and the target's conditions count in a roll
                # made here; one typed in gets what it couldn't count.
                typed = effect.typed_attacks.get(id(target))
                if typed is None:
                    # What others answer it with before it's rolled (Warding
                    # Flare's Disadvantage), counted in the roll.
                    self._before_attack_roll(source, target)
                # Where the two are on the map settles Prone's "within 5
                # feet" in the roll, and Paralyzed's Critical Hit.
                feet = self._attacker_distance_ft(source, target)
                # Its range too: Long range's Disadvantage counted, past
                # its reach or range warned about (Combat/Arena/ranges.py).
                reach = self._range_check(
                    source, target, pick_attack_range(effect.pick, source)
                )
                plan = attack_plan(
                    source,
                    target,
                    effect.mode,
                    typed is not None,
                    feet,
                    reach.modifiers,
                    reach.sight,
                )
                if typed is not None:
                    roll, notes = typed, plan.notes
                else:
                    roll, notes = roll_planned_attack(effect.attack_bonus, plan)
                notes = (*notes, *reach.notes, *reach.warnings)
                hit, attack = self._resolve_attack_roll(
                    target, roll, source, notes, _ignores_cover(effect.pick)
                )
                critical = roll.is_critical or (
                    hit is not False and self._critical_against(source, target)
                )
                reduction = 0
                if hit is not False and source is not None:
                    # What the target answers the hit with (Shield, Deflect
                    # Attacks), before its damage.
                    still, reduction = self._before_hit(
                        AttackOutcome(
                            source,
                            target,
                            hit,
                            critical=critical,
                            kind=kind,
                            row=picked_row,
                            total=roll.total,
                            armor=armor_in_use(
                                self._covered(
                                    source, target, None, _ignores_cover(effect.pick)
                                )
                            ),
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
                if critical:
                    damage = effect.critical_damage or damage
                if damage:
                    damage = self._with_hit_extras(
                        source, target, damage, effect, critical
                    )
                if reduction:
                    damage = reduced_damage(damage, reduction)
            if effect.ability is not None:
                saved = self._roll_effect_save(target, effect, source)
                results.append(saved)
            avoided = effect.ability is not None and saved and not effect.half_on_save
            dealt = 0
            if damage and not avoided:
                dealt = self._deal_damage(
                    target,
                    damage,
                    source,
                    effect.count_resistances,
                    saved,
                    critical=critical,
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
            if effect.push is not None and target is not source:
                to_push.append(target)
            # What it ends (Lay on Hands' Poisoned) goes from the same targets
            # its conditions would land on.
            for condition in effect.pick.ends_conditions if effect.pick else ():
                if condition in target["conditions"]:
                    self._remove_condition_from(target, condition, source=source)
            applied += self._give_effect_conditions(target, effect)

        pick = effect.pick
        if pick is not None and pick.is_described and source is not None:
            # What comes after this row of its source, on each of its targets
            # (USES: Ice Knife's explosion after its shard, hit or miss).
            for target in living:
                if any(target is c for c in self.characters):
                    self._after_attack(UsesOutcome(source, target, pick.name))
        if effect.concentration and caster is not None:
            self._hold_concentration(caster, label, effect, applied)
        elif effect.area is not None and source is not None:
            self._hold_area(source, label, effect)
        elif effect.from_area:
            self._hold_with_area(effect.from_area, applied)
        if effect.damage and source is not None:
            source["_last_damage_type"] = effect.damage[0][1]  # not an extra's
        pushed = []
        if effect.push is not None and source is not None and to_push:
            pushed = self._push_targets(source, effect.push, to_push, label)
        self._saved_targets = []
        self._update_target_label()
        for target in self.target_characters:
            self._rebuild_card(target)
        self._save_fight_state()
        self._show_effect_summary(effect, results)
        if pushed:
            self._refresh_views()  # the tokens where they were pushed to
        elif logged_use and effect.pick is not None and effect.pick.monster_action:
            self._refresh_views()  # the turn column's button shows it spent
        if attacks or pushed:  # last, as logging clears the status line
            self._show_status(" ".join(filter(None, ["; ".join(attacks), *pushed])))

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

    def _set_shield(self, char: dict, wielding: bool | None):
        """Have char wield its Shield or set it down (the attack rows' Shield
        box), with a log line when that changes it. None, or a char without
        a Shield, leaves it as it is. It stays so until changed again."""
        if wielding is None or not has_shield(char):
            return
        if wielding != is_shield_off(char):
            return
        if wielding:
            char.pop(SHIELD_OFF, None)
        else:
            char[SHIELD_OFF] = True
        did = "takes up" if wielding else "sets down"
        self._log_event(f"{char['name']} {did} a Shield", character=char["name"])
        self._rebuild_card(char)

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

    def _regain_feature_uses(self, char: dict, option: EffectOption):
        """Give char back the expended feature uses option regains
        (Uncanny Metabolism's Focus Points), a logged line per use, as a rest
        logs them, so the party's history replays them."""
        used = char.setdefault("feature_uses_used", {})
        for regain in option.regains:
            for _ in range(regained_uses(char, regain)):
                used[regain.feature] = max(used.get(regain.feature, 0) - 1, 0)
                self._log_event(
                    f"{char['name']} regains a use of {regain.feature}"
                    f" ({option.name})",
                    character=char["name"],
                    action=Action.REGAIN_FEATURE_CHARGE,
                    value=regain.feature,
                )
        self._rebuild_card(char)

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
                caster,
                option.feature_name or option.name,
                option.counts_uses,
                count=option.uses_spent,
            )
            return True
        if option.monster_action is not None:
            # _apply_custom_effect asked already if it's spent (_effect_lacks).
            return self._spend_monster_action(caster, option.monster_action, ask=False)
        if option.kind == STANDARD_ACTION:
            # "Clover takes the Help action (Assist an Attack Roll)".
            action, _, how = option.name.partition(": ")
            how = f" ({how})" if how else ""
            self._log_event(
                f"{caster['name']} takes the {action} action{how}",
                character=caster["name"],
            )
            return True
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
            lacks.insert(
                0,
                feature_lack(
                    caster, option.feature_name or option.name, option.uses_spent
                ),
            )
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
        """Caster's concentration on the effect, tied to what it put on whom,
        and the area it keeps on the map, if any (arena step 11). If the
        effect itself just ended that concentration (the caster was among
        its targets), it's over already."""
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
            # With a turn for a duration, the conditions are what end first;
            # not while an area on the map lasts with the concentration.
            "ends_with_conditions": "until" in duration
            and bool(applied)
            and effect.area is None,
        }
        if effect.area is not None:
            entry[AREA_KEY] = effect.area
        if CombatStatus.CONCENTRATING.value not in caster["conditions"]:
            self._end_spell_effects(entry)
            return
        caster.setdefault("active_spells", []).append(entry)
        self._link_concentration(caster, applied)
        if effect.area is not None:
            self._log_area_kept(caster, label, effect.area)
        self._rebuild_card(caster)

    def _hold_with_area(self, key: str, applied: list[dict]):
        """What a kept area gave as it acted again (Web's Restrained), held
        by the area's active spell when its caster concentrates on it, so
        it comes off as the concentration ends, as what the cast gave does."""
        found = find_area(self.characters, key)
        if found is None or not applied:
            return
        caster, entry = found
        if not entry.get("concentration"):
            return
        held = entry.setdefault("applied", [])
        new = [row for row in applied if row not in held]
        held.extend(new)
        self._link_concentration(caster, new)

    def _link_concentration(self, caster: dict, applied: list[dict]):
        """Record on each effect in `applied` ({"target", "condition"} rows,
        as an active spell holds them) that caster concentrates on it."""
        for row in applied:
            target = self._find_character_by_name(row["target"])
            if target is not None:
                link_concentration(target, row["condition"], caster["name"])

    def _give_effect_conditions(self, target: dict, effect: CustomEffect) -> list[dict]:
        """Give target every condition of effect that lands (one it's immune
        to doesn't), its pick's badge and its repeat save: what the Custom
        Effect dialog does to a target it hit or that failed its save, and a
        monster's action button to the target its hit lands on. Returns the
        ({"target", "condition"}) rows a running effect now holds."""
        applied, linked = [], []
        for condition in effect.conditions:
            row = {"target": target["name"], "condition": condition}
            already_had = condition in target["conditions"]
            held_by_a_spell = self._held_by_effect(row)
            held_by_a_badge = is_linked(target, condition)
            if self._give_effect_condition(target, effect, condition):
                if held_by_a_spell or not already_had:
                    applied.append(row)
                if held_by_a_badge or not already_had:
                    linked.append(condition)
        self._give_pick_badge(target, effect, linked)
        if effect.repeat_save and effect.ability is not None:
            self._track_repeat_save(target, effect)
        return applied

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
        duration = effect.duration
        if effect.pick is not None:
            duration = effect.pick.duration_for(condition, duration)
        self._add_custom_condition(condition, duration, effect.notes, [target])
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
                rolled_maximum=effect.typed_hit_point_maximum.get(id(target)),
            )
            if source is not None:
                note_origin(
                    target, condition, source=effect.name, caster=source["name"]
                )
        return True

    def _picked_feature(self, owner: dict, option: EffectOption):
        """owner's feature object for a picked feature row: the row's own
        feature (Hill's Tumble), else the one whose uses it spends."""
        features = owner.get("_feature_objects", [])
        for name in (option.name, option.feature_name):
            feature = next((f for f in features if f.name == name), None)
            if feature is not None:
                return feature
        return None

    def _give_pick_badge(
        self, target: dict, effect: CustomEffect, conditions: list[str]
    ):
        """Beside the rules conditions a picked spell or feature just gave
        target (Friends' Charmed, Turn Undead's Frightened), a badge of the
        spell's or feature's own name with its card, so the card says where
        they're from. It stands for `conditions`: it comes off with the last
        of them, and they come off with it (link_badge). None for a pick
        whose badge is its own name already (Bless), a weapon's or a
        monster's action (its rider is plain in the log), or conditions that
        aren't rules conditions (Hexed)."""
        option = effect.pick
        if option is None:
            return
        rules = [c for c in conditions if ConditionRule.from_name(c) is not None]
        if not rules:
            return
        if HIDDEN in effect.conditions and HIDDEN in target["conditions"]:
            # The Hide action's (or Cunning Action's): Hidden stands for the
            # Invisible it came with, so its next attack roll ends both.
            link_badge(target, HIDDEN, rules)
            return
        source = self.selected_character or self._current_turn_character()
        # A spell's badge, for a spell or a feature's use that casts one.
        badge = option.spell_name or (option.name if option.kind == SPELL else "")
        if badge:
            spell = self._spell_named(badge)
            if spell is not None and badge not in effect.conditions:
                describe(
                    target,
                    badge,
                    spell_badge_description(spell),
                    spell_badge_color(spell),
                    SPELL,
                )
        elif option.kind == FEATURE:
            badge = option.name
            feature = (
                self._picked_feature(source, option) if source is not None else None
            )
            if (
                source is not None
                and feature is not None
                and badge not in effect.conditions
            ):
                describe(
                    target,
                    badge,
                    self._feature_condition_tooltip(source, feature),
                    FEATURE_BADGE_COLOR,
                    FEATURE,
                )
        if not badge or badge in effect.conditions:
            return
        self._add_condition_to(target, badge, source=source, counted=False)
        link_badge(target, badge, conditions)
        note_origin(
            target,
            badge,
            source=effect.name or badge,
            caster=source["name"] if source is not None else None,
        )

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
            feature = self._picked_feature(owner, option)
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

    def _roll_effect_save(
        self, target: dict, effect: CustomEffect, source: dict | None = None
    ) -> bool:
        """Target's save against the effect, logged. Legendary Resistance turns
        a failure into a success, if the dialog said to use it. The map's
        cover counts in a Dexterity save: from source, or from the area's
        point of origin (effect.cover_origin)."""
        assert effect.ability is not None  # the caller checks
        name = target["name"]
        result = roll_save(
            self._covered(
                source, target, effect.cover_origin, _ignores_cover(effect.pick)
            ),
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
        if result.total is not None and id(target) not in effect.typed_totals:
            # What target answers a failed save rolled here with (Indomitable);
            # one rolled at the table is rerolled there.
            failed = FailedSaveOutcome(
                target, effect.ability, effect.dc, result.total, effect.name
            )
            if self._reroll_failed_save(failed, effect):
                return True
        if effect.use_legendary_resistance and legendary_resistances_left(target) > 0:
            self._use_legendary_resistance(target)
            return True
        return False

    def _reroll_failed_save(
        self, failed: FailedSaveOutcome, effect: CustomEffect
    ) -> bool:
        """Ask the creature that failed a save rolled here about its FAILS_SAVE
        rows (Indomitable), now, in a pop-up of its own; one applied spends its
        use, and the save is rolled again with its bonus, which it must keep.
        Returns whether the new roll succeeds. With the setting ask_triggers
        off, it's a turn-column button instead, and the save stays failed."""
        found, spent = outcome_firings([failed], triggered_rows)
        found = [f for f in found if f.row.reroll_save is not None]
        if not found:
            return False
        if not self.settings.ask_triggers:
            self._hit_prompts = (*self._hit_prompts, *found)
            self._refresh_turn_prompts()
            return False
        status = self._status_label.text()
        notes = list(spent)
        applied = self._answer_firings(found[:1], notes)
        success = False
        for firing, at_table in applied:
            bonus = firing.row.reroll_save or 0
            plus = f" + {bonus}" if bonus else ""
            if at_table is not None:
                # The new total as rolled at the table, the bonus in it.
                total, how = at_table, f"{at_table}, rolled at the table"
            else:
                again = roll_save(failed.char, failed.ability, failed.dc, effect.mode)
                if again.total is None:
                    continue
                total = again.total + bonus
                how = f"{again.total}{plus} = {total}"
            success = total >= failed.dc
            verb = "makes" if success else "fails"
            self._log_event(
                f"{failed.char['name']} rerolls the save with {firing.row.name}:"
                f" {how}, {verb} it",
                character=failed.char["name"],
            )
        self._show_status("; ".join(part for part in (status, *notes) if part))
        return success

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

    def _show_custom_condition_dialog(
        self, pick: str = "", cost: str | None = None, kept_area: str = ""
    ):
        """Set up an effect on every target (see _apply_custom_effect): what
        it costs the source, a saving throw or an attack roll, damage, and a
        condition with its duration and a note. What the source can use is
        listed on the left, and a pick fills in the form. `pick` names a row
        to start with picked (a trigger's prompt: "Spirit Guardians:
        damage"). `cost`, if given, is what using it costs whatever row is
        picked (an Opportunity Attack's Reaction). An area just aimed on the
        map for it (ArenaMixin's _aimed_area) is offered to keep on the map,
        and kept, it can be applied with no targets (Moonbeam put on empty
        ground). `kept_area`, the key of an area kept on the map, makes it
        that area acting again (its turn-column prompt, arena step 24): it
        costs nothing, as its cast was spent, its damage is at the slot it
        was cast with, the map's cover is counted from where it was aimed,
        and a condition it gives is held by its concentration.

        It opens with or without targets: a box per target at the top,
        prefilled with the targets picked on the cards or the map, picks
        anyone, + adds a box (up to what the pick may target) and × takes one
        away. A pick that needs a target says "Target: missing" while it has
        none, and Apply makes the boxes' picks the targets."""
        _UseCastDialog(self).run(pick, cost, kept_area)

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
        if self.phase == Phase.PARTY:
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
        if action_type == ActionCost.REACTION:
            # Its other Opportunity Attack buttons go: the Reaction is spent
            # (arena step 23).
            left = tuple(
                p
                for p in self._hit_prompts
                if not (isinstance(p, OpportunityAttack) and p.attacker is char)
            )
            if len(left) != len(self._hit_prompts):
                self._hit_prompts = left
                self._refresh_turn_prompts()
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


class _UseCastDialog:
    """The Use / Cast dialog, one opening of it: what
    ConditionsMixin._show_custom_condition_dialog says it does. It was that
    function, with its nested functions (Notes/combat-ui-refactor-plan.md,
    step 3b): what they shared is attributes now, and they are methods.
    `app` is the window it opens over."""

    def __init__(self, app: ConditionsMixin):
        self.app = app

    def run(self, pick: str, cost: str | None, kept_area: str):
        self.cost = cost
        self.kept_area = kept_area
        self.source = self.app.selected_character or self.app._current_turn_character()
        self.aimed, self.app._aimed_area = self.app._aimed_area, None
        if self.aimed is not None and (
            self.source is None or self.aimed["source"] != self.source["name"]
        ):
            self.aimed = None
        # The kept area acting again, if this is its prompt: it spends nothing.
        self.again = (
            find_area(self.app.characters, self.kept_area) if self.kept_area else None
        )
        again_record: dict | None = (
            self.again[1][AREA_KEY] if self.again is not None else None
        )
        self.again_level = (again_record or {}).get("slot_level")
        if again_record is not None:
            self.aimed = None
        # The map's cover against a save is counted from where the aimed
        # area spreads (a Fireball's cell), else from the source.
        self.cover_origin = (
            record_origin(self.aimed["record"]) if self.aimed is not None else None
        )
        if again_record is not None:
            self.cover_origin = record_origin(again_record)
        self.caster = self.app.selected_character
        # The targets as the boxes at the top pick them, changed in place.
        self.targets: list[dict] = list(self.app.target_characters)
        self.choices = list(self.app.characters)
        self.source_name = self.source["name"] if self.source is not None else ""
        # The pick, and the damage and search it was made with, to tell the
        # GM's edits by.
        self.picked: dict = {"option": None, "damage": "", "times": 1, "search": ""}

        self.dlg = QDialog(self.app._window)
        self.dlg.setObjectName("customEffectDialog")
        self.dlg.setWindowTitle("Use / Cast")
        self.dlg.setMinimumWidth(_CUSTOM_DIALOG_WIDTH)
        self.dlg.resize(_effect_dialog_width(self.app._window), 0)
        outer = QVBoxLayout(self.dlg)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(10)

        # Who uses it on whom: the source, then a box per target.
        who_row = QHBoxLayout()
        who_row.setSpacing(8)
        outer.addLayout(who_row)
        who_lbl = QLabel(_source_text(self.source))
        who_lbl.setObjectName("effectWho")
        who_lbl.setTextFormat(Qt.TextFormat.RichText)
        who_lbl.setToolTip("Left-click a card for the source before opening this.")
        who_row.addWidget(who_lbl, alignment=Qt.AlignmentFlag.AlignTop)
        self.target_boxes = QWidget()
        self.target_boxes.setObjectName("effectTargets")
        self.target_grid = QGridLayout(self.target_boxes)
        self.target_grid.setContentsMargins(0, 0, 0, 0)
        self.target_grid.setHorizontalSpacing(6)
        self.target_grid.setVerticalSpacing(4)
        self.target_grid.setColumnStretch(_TARGETS_PER_LINE + 1, 1)
        who_row.addWidget(self.target_boxes, stretch=1)
        # A pick that goes on its user (Second Wind) instead of the boxes.
        self.itself_lbl = QLabel("")
        self.itself_lbl.setObjectName("targetItself")
        self.itself_lbl.hide()
        who_row.addWidget(
            self.itself_lbl, stretch=1, alignment=Qt.AlignmentFlag.AlignTop
        )
        self.add_target_btn = QPushButton("+")
        self.add_target_btn.setObjectName("addTarget")
        self.add_target_btn.setAutoDefault(False)
        self.add_target_btn.setFixedWidth(_TARGET_BUTTON_WIDTH)
        self.missing_lbl = QLabel("Target: missing")
        self.missing_lbl.setObjectName("targetMissing")
        self.missing_lbl.setToolTip("Pick who it's used on in a box to the left.")
        # Each box and the row holding it with its × button, in order.
        self.target_slots: list[tuple[QWidget, QComboBox]] = []

        self.add_target_btn.clicked.connect(self.add_empty_target_slot)
        for target in self.targets or [None]:
            self.add_target_slot(target)

        body = QHBoxLayout()
        body.setSpacing(14)
        outer.addLayout(body, stretch=1)

        # What the source can use, on the left: a pick fills in the form, and
        # its rules text shows under the list.
        self.search_box, self.tree, self.category_items = self.app._effect_picker(
            self.source
        )
        self.details = QTextBrowser()
        self.details.setObjectName("effectDetails")
        self.details.setOpenLinks(False)
        self.details.setMinimumHeight(_DETAILS_MIN_HEIGHT)
        picker_box = QWidget()
        picker_box.setFixedWidth(_PICKER_WIDTH)
        picker = QVBoxLayout(picker_box)
        picker.setContentsMargins(0, 0, 0, 0)
        picker.setSpacing(6)
        picker.addWidget(self.search_box)
        picker.addWidget(self.tree, stretch=3)
        picker.addWidget(self.details, stretch=2)
        body.addWidget(picker_box)

        form = QVBoxLayout()
        form.setSpacing(8)
        body.addLayout(form, stretch=1)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("effectName")
        self.name_input.setPlaceholderText("Name for the log (optional), e.g. Fireball")
        form.addWidget(self.name_input)

        # What to check about a pick, and what a monster's action does besides.
        self.note_lbl = QLabel("")
        self.note_lbl.setObjectName("effectNote")
        self.note_lbl.setWordWrap(True)
        self.note_lbl.hide()
        form.addWidget(self.note_lbl)

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
        self.roll_combo = QComboBox()
        self.roll_combo.setObjectName("rollKind")
        self.roll_combo.addItems((SAVING_THROW, ATTACK_ROLL))
        self.roll_combo.setCurrentText(self.app._custom_save["roll"])
        self.roll_combo.hide()
        roll_box.addWidget(self.roll_combo)
        self.ability_combo = QComboBox()
        self.ability_combo.setObjectName("saveAbility")
        self.ability_combo.addItem("No saving throw", None)
        for full, short in ABILITIES:
            self.ability_combo.addItem(full, short)
        self.ability_combo.setCurrentIndex(
            max(self.ability_combo.findData(self.app._custom_save["ability"]), 0)
        )
        roll_box.addWidget(self.ability_combo)

        kind_row, kind_layout = row_widget("rollKindButtons")
        kind_layout.setSpacing(3)
        self.kind_buttons = {
            NO_ROLL: chip("&No roll", "Damage and the condition for everyone (Alt+N)"),
            SAVING_THROW: chip("&Saving throw", "Each target saves (Alt+S)"),
            ATTACK_ROLL: chip(
                "&Attack roll", "The source rolls against each target's AC (Alt+A)"
            ),
        }
        for button in self.kind_buttons.values():
            button.setProperty("rollKind", True)
            kind_layout.addWidget(button, stretch=1)
        roll_box.addWidget(kind_row)

        self.save_line, save_layout = row_widget()
        save_layout.setSpacing(8)
        ability_chips = chip_row(
            self.ability_combo,
            [(i, short, full) for i, (full, short) in enumerate(ABILITIES, start=1)],
            "saveAbilityButtons",
        )
        save_layout.addWidget(ability_chips, stretch=1)
        self.dc_label = QLabel("DC")
        save_layout.addWidget(self.dc_label)
        self.dc_input = QSpinBox()
        self.dc_input.setObjectName("saveDc")
        self.dc_input.setRange(1, MAX_SAVE_DC)
        same_source = self.app._custom_save["source"] is self.source
        known_dc = None if same_source else known_save_dc(self.source)
        self.dc_input.setValue(known_dc or self.app._custom_save["dc"])
        save_layout.addWidget(self.dc_input)
        roll_box.addWidget(self.save_line)

        self.attack_line, attack_layout = row_widget()
        bonus_label = QLabel("Attack bonus")
        attack_layout.addWidget(bonus_label)
        self.bonus_input = QSpinBox()
        self.bonus_input.setObjectName("attackBonus")
        self.bonus_input.setRange(MIN_ATTACK_BONUS, MAX_ATTACK_BONUS)
        self.bonus_input.setToolTip("What the source adds to its d20")
        known_bonus = None if same_source else known_attack_bonus(self.source)
        self.bonus_input.setValue(
            self.app._custom_save["bonus"] if known_bonus is None else known_bonus
        )
        attack_layout.addWidget(self.bonus_input)
        attack_layout.addStretch()
        roll_box.addWidget(self.attack_line)

        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("saveMode")
        self.mode_combo.addItems(ROLL_MODES)
        roll_box.addWidget(self.mode_combo)
        self.mode_chips = chip_row(
            self.mode_combo,
            [
                (0, "Neutral", "One d20"),
                (1, "Advantage", "Two d20s, the higher counts, for every target"),
                (2, "Disadvantage", "Two d20s, the lower counts, for every target"),
            ],
            "saveModeButtons",
        )
        roll_box.addWidget(self.mode_chips)

        self.half_box = QCheckBox("Half damage on a save")
        self.half_box.setObjectName("halfOnSave")
        self.half_box.setChecked(self.app._custom_save["half"])
        roll_box.addWidget(self.half_box)

        self.repeat_box = QCheckBox("Repeat the save at the end of each turn")
        self.repeat_box.setObjectName("repeatSave")
        self.repeat_box.setToolTip(
            "A save ends the condition. Monsters roll by themselves; players"
            " get a reminder."
        )
        roll_box.addWidget(self.repeat_box)

        self.resist_box = QCheckBox("Use Legendary Resistance on a failed save")
        self.resist_box.setObjectName("useLegendaryResistance")
        roll_box.addWidget(self.resist_box)

        # A roll made at the table is typed in; the rest are rolled. Each target
        # rolls a save for itself, and the source an attack against each one.
        self.rolls_hint = QLabel("Rolled at the table? Type it; blank rolls.")
        self.rolls_hint.setObjectName("secondary")
        roll_box.addWidget(self.rolls_hint)
        # The rows per target, built again whenever the targets change: the
        # boxes and labels by id(target), filled in place so what reads them
        # always has the current ones.
        rolls_holder = QWidget()
        self.rolls_layout = QVBoxLayout(rolls_holder)
        self.rolls_layout.setContentsMargins(0, 0, 0, 0)
        self.rolls_layout.setSpacing(6)
        roll_box.addWidget(rolls_holder)
        self.roll_rows: dict[str, QWidget] = {}
        self.typed_inputs: dict[int, QLineEdit] = {}
        self.save_infos: dict[int, QLabel] = {}
        self.attack_inputs: dict[int, QLineEdit] = {}
        self.attack_infos: dict[int, QLabel] = {}
        self.extra_rows: dict = {}
        self.shield_boxes: dict[int, QCheckBox] = {}

        self.build_roll_rows()
        roll_col.addStretch()

        # ── Damage, or Hit Points regained, or Temporary Hit Points
        damage_frame, damage_box, self.amount_header = section("Damage")
        effect_col.addWidget(damage_frame)
        self.amount_combo = QComboBox()
        self.amount_combo.setObjectName("amountKind")
        self.amount_combo.addItems(AMOUNT_KINDS)
        damage_box.addWidget(self.amount_combo)
        amount_chips = chip_row(
            self.amount_combo,
            [
                (0, DAMAGE_AMOUNT, "Each target it lands on takes it"),
                (1, HEALING, "Every target regains it, whatever the roll"),
                (2, TEMP_HP, "Every target gains it, whatever the roll"),
            ],
            "amountKindButtons",
        )
        damage_box.addWidget(amount_chips)
        damage_row = QHBoxLayout()
        self.damage_input = QLineEdit()
        self.damage_input.setObjectName("effectDamage")
        self.damage_input.setPlaceholderText("e.g. 8d6, 28, 2d6 sl + 1d4 fi")
        self.damage_input.setToolTip("Dice are rolled once, for everyone it hits")
        damage_row.addWidget(self.damage_input, stretch=3)
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("damageType")
        self.type_combo.addItem("— Type —", None)
        for damage_type in DamageType:
            self.type_combo.addItem(damage_type.value, damage_type.value)
        if self.source is not None and self.app.settings.remember_damage_type:
            self.type_combo.setCurrentIndex(
                max(self.type_combo.findData(self.source.get("_last_damage_type")), 0)
            )
        damage_row.addWidget(self.type_combo, stretch=2)
        damage_box.addLayout(damage_row)

        self.resistances_box = QCheckBox("Count resistances and immunities")
        self.resistances_box.setObjectName("countResistances")
        self.resistances_box.setChecked(True)
        damage_box.addWidget(self.resistances_box)
        times_line, times_layout = row_widget()
        times_layout.addWidget(QLabel("Times"))
        self.times_input = QSpinBox()
        self.times_input.setObjectName("effectTimes")
        self.times_input.setRange(1, MAX_EFFECT_TIMES)
        self.times_input.setToolTip(
            "Repeat it against each target, each time with its own attack roll,"
            " save and damage roll (Scorching Ray's rays, Eldritch Blast's"
            " beams). It costs the source once."
        )
        times_layout.addWidget(self.times_input)
        times_layout.addStretch()
        damage_box.addWidget(times_line)

        # ── Condition
        condition_frame, condition_box, self.condition_header = section("Condition")
        effect_col.addWidget(condition_frame)
        self.name_combo = QComboBox()
        self.name_combo.setObjectName("conditionName")
        self.name_combo.setEditable(True)
        self.name_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.suggestions = self.app._custom_condition_suggestions()
        self.name_combo.addItems(self.suggestions)
        self.name_combo.setCurrentText("")
        name_edit = self.name_combo.lineEdit()
        assert name_edit is not None  # an editable combo box has one
        name_edit.setPlaceholderText("e.g. Hexed, Restrained by vines, -2 AC...")
        condition_box.addWidget(self.name_combo)

        self.notes_input = QLineEdit()
        self.notes_input.setObjectName("conditionNotes")
        self.notes_input.setPlaceholderText("Notes (optional, shown on hover)")
        condition_box.addWidget(self.notes_input)

        # A Hit Point maximum the badge rolls (Heroes' Feast's 2d10), rolled at
        # the table instead (plan step 8.6); shown for a pick that has one.
        self.maximum_input = QLineEdit()
        self.maximum_input.setObjectName("typedHitPointMaximum")
        self.maximum_input.setToolTip(
            "The Hit Point maximum rolled at the table, upcast and all: one"
            " total for every target, or one per target in the order they're"
            " listed (12, 9, 15). Blank rolls it for each."
        )
        self.maximum_input.hide()
        condition_box.addWidget(self.maximum_input)

        self.duration_combo = QComboBox()
        self.duration_combo.setObjectName("conditionDuration")
        self.duration_combo.setToolTip("How long the condition lasts")
        for label, duration in CUSTOM_CONDITION_DURATIONS:
            if duration is not None and duration.get("of") == "source":
                if self.source is None:
                    continue
                label = label.format(source=self.source["name"])
            self.duration_combo.addItem(label, duration)
        self.duration_combo.addItem("Custom...", "custom")
        condition_box.addWidget(self.duration_combo)

        custom_row = QHBoxLayout()
        self.amount_input = QSpinBox()
        self.amount_input.setObjectName("durationAmount")
        self.amount_input.setRange(1, MAX_DURATION_AMOUNT)
        custom_row.addWidget(self.amount_input)
        self.unit_combo = QComboBox()
        self.unit_combo.setObjectName("durationUnit")
        self.unit_combo.addItems(list(CUSTOM_DURATION_UNITS))
        custom_row.addWidget(self.unit_combo, stretch=1)
        self.custom_widgets = (self.amount_input, self.unit_combo)
        condition_box.addLayout(custom_row)

        # ── What it costs the source
        cost_title = (
            f"Cost to {self.caster['name']}" if self.caster is not None else "Cost"
        )
        cost_frame, cost_box, _ = section(cost_title)
        effect_col.addWidget(cost_frame)
        self.slot_combo = QComboBox()
        self.slot_combo.setObjectName("spellSlot")
        self.slot_combo.addItem("No spell slot", None)
        for label, level in spell_slot_choices(self.caster or {}, 1):
            if level is not None:
                self.slot_combo.addItem(label, level)
        cost_box.addWidget(self.slot_combo)
        # How many creatures the pick may target (Bless: 3), at the slot chosen.
        self.target_count_lbl = QLabel("")
        self.target_count_lbl.setObjectName("targetCount")
        self.target_count_lbl.setWordWrap(True)
        self.target_count_lbl.hide()
        cost_box.addWidget(self.target_count_lbl)
        self.action_combo = QComboBox()
        self.action_combo.setObjectName("actionCost")
        self.action_combo.addItem("No action", None)
        for action_type in self.app.ACTION_ECONOMY_TYPES:
            self.action_combo.addItem(action_type, str(action_type))
        cost_box.addWidget(self.action_combo)
        action_chips = chip_row(
            self.action_combo,
            [(0, "None", "Spends no action")]
            + [
                (i, action_type, f"Spends the source's {action_type}")
                for i, action_type in enumerate(self.app.ACTION_ECONOMY_TYPES, start=1)
            ],
            "actionCostButtons",
        )
        cost_box.addWidget(action_chips)
        self.concentrate_box = QCheckBox("Source concentrates on it")
        self.concentrate_box.setObjectName("sourceConcentrates")
        self.concentrate_box.setToolTip(
            "Starts Concentrating, ending any other concentration. When it"
            " ends, the condition comes off the targets."
        )
        cost_box.addWidget(self.concentrate_box)
        # The area aimed on the map, to keep there (arena step 11).
        self.keep_area_box = QCheckBox(
            f"Keep the {self.aimed['text']} on the map"
            if self.aimed
            else "Keep the area"
        )
        self.keep_area_box.setObjectName("keepArea")
        self.keep_area_box.setToolTip(
            "The area stays on the map in its colour, as one of the source's"
            " Active Spells: for as long as the effect lasts, and with"
            " 'Source concentrates on it', until concentration ends."
        )
        self.keep_area_box.setChecked(bool(self.aimed and self.aimed["keep"]))
        self.keep_area_box.setVisible(self.aimed is not None)
        cost_box.addWidget(self.keep_area_box)
        # A pick that moves who it lands on (CombatEffect.push), once the map
        # is in use with the source on it (arena step 21).
        self.push_box = QCheckBox("")
        self.push_box.setObjectName("pushTargets")
        self.push_box.setToolTip(
            "Moves each target that fails the save or is hit (every target with"
            " no roll) straight away from the source on the battle map, as a"
            " push: no movement spent, no Opportunity Attack. It stops short"
            " of a wall, the map's edge or someone's space. 'Up to': the whole"
            " way here; Alt-drag a token back for less."
        )
        self.push_box.setChecked(True)
        self.push_box.hide()
        cost_box.addWidget(self.push_box)
        self.pushes_on_map = (
            self.app.phase == Phase.COMBAT
            and self.source is not None
            and position(self.source) is not None
            and self.app.arena_settings.in_use
        )

        for widget in (self.slot_combo, self.action_combo, self.concentrate_box):
            widget.setEnabled(self.caster is not None and self.again is None)
        if self.again is not None:
            at = f", at level {int(self.again_level)}" if self.again_level else ""
            free_lbl = QLabel(
                f"{self.again[0]['name']}'s {self.again[1]['name']} acting again: its"
                f" cast is spent already, so this costs nothing{at}."
            )
            free_lbl.setObjectName("keptAreaFree")
            free_lbl.setWordWrap(True)
            cost_box.addWidget(free_lbl)
        if self.caster is None:
            no_cost = QLabel("No source picked: left-click a card to spend from it.")
            no_cost.setObjectName("secondary")
            no_cost.setWordWrap(True)
            cost_box.addWidget(no_cost)
        effect_col.addStretch()

        # ── What Apply will do, what's wrong, and the buttons
        self.preview_lbl = QLabel("")
        self.preview_lbl.setObjectName("effectPreview")
        self.preview_lbl.setWordWrap(True)
        outer.addWidget(self.preview_lbl)

        btn_row = QHBoxLayout()
        footer = QVBoxLayout()
        footer.setSpacing(2)
        self.problem_lbl = QLabel("")
        self.problem_lbl.setObjectName("statusLabel")
        self.problem_lbl.setWordWrap(True)
        footer.addWidget(self.problem_lbl)
        keys_lbl = QLabel(
            "↑↓ browse · Enter picks, again applies · Ctrl+Enter apply"
            " · Alt+N/S/A roll · Ctrl+F search"
        )
        keys_lbl.setObjectName("secondary")
        footer.addWidget(keys_lbl)
        btn_row.addLayout(footer, stretch=1)
        # Targets in an area: the map aims the pick's area, and this dialog
        # opens again on the same pick with whoever is in it (arena step 10).
        area_btn = QPushButton("Select targets in a&rea")
        area_btn.setObjectName("areaTargetsBtn")
        area_btn.setAutoDefault(False)
        on_map = (
            self.app.phase == Phase.COMBAT
            and self.source is not None
            and position(self.source) is not None
        )
        area_btn.setEnabled(on_map)
        area_btn.setToolTip(
            "Aim the area on the map: whoever is in it becomes the targets,"
            " and this opens again on the same pick (Alt+R)"
            if on_map
            else "Needs a fight with the source on the map"
        )
        self.area_request: list[bool] = []

        area_btn.clicked.connect(self.select_in_area)
        btn_row.addWidget(area_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setAutoDefault(False)
        cancel_btn.setMinimumWidth(_BUTTON_WIDTH)
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setObjectName("primaryBtn")
        self.apply_btn.setAutoDefault(False)
        self.apply_btn.setMinimumWidth(_BUTTON_WIDTH)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.apply_btn)
        outer.addLayout(btn_row)

        # The ability a saving throw goes back to after "No roll".
        self.last_ability = {"value": self.ability_combo.currentData() or "DEX"}

        for kind, button in self.kind_buttons.items():
            button.clicked.connect(lambda _=False, k=kind: self.choose_kind(k))

        self.duration_combo.currentIndexChanged.connect(self.show_custom_row)
        self.roll_combo.currentIndexChanged.connect(self.show_roll_controls)
        self.ability_combo.currentIndexChanged.connect(self.show_roll_controls)
        self.amount_combo.currentIndexChanged.connect(self.show_amount_controls)
        self.amount_combo.currentIndexChanged.connect(self.show_roll_controls)
        self.damage_input.textChanged.connect(self.show_typed_type)
        for signal in (
            self.amount_combo.currentIndexChanged,
            self.roll_combo.currentIndexChanged,
            self.ability_combo.currentIndexChanged,
            self.mode_combo.currentIndexChanged,
            self.dc_input.valueChanged,
            self.bonus_input.valueChanged,
            self.half_box.toggled,
            self.repeat_box.toggled,
            self.damage_input.textChanged,
            self.type_combo.currentIndexChanged,
            self.name_combo.currentTextChanged,
            self.duration_combo.currentIndexChanged,
            self.amount_input.valueChanged,
            self.unit_combo.currentIndexChanged,
            self.slot_combo.currentIndexChanged,
            self.action_combo.currentIndexChanged,
            self.concentrate_box.toggled,
        ):
            signal.connect(self.show_preview)
        self.show_custom_row()
        self.show_amount_controls()
        self.show_roll_controls()
        self.show_preview()

        # Enter in a text box and the Apply button can both fire; apply once.
        self.applied: list[bool] = []

        # The rolls typed for each of the Times, as do_apply read them.
        self.typed_rolls: dict[str, dict] = {"totals": {}, "attacks": {}, "extras": {}}

        # Up and Down from the search box pick as they go (fill_from), so
        # Enter applies the row they reached.
        SearchKeys(self.search_box, self.tree)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.tree.currentItemChanged.connect(self.on_current_changed)
        self.tree.itemActivated.connect(self.item_activated)
        self.search_box.returnPressed.connect(self.search_entered)
        self.slot_combo.currentIndexChanged.connect(self.upcast)
        self.name_input.textEdited.connect(self.drop_pick)

        self.apply_btn.clicked.connect(self.do_apply)
        name_edit.returnPressed.connect(self.do_apply)
        self.notes_input.returnPressed.connect(self.do_apply)
        self.damage_input.returnPressed.connect(self.do_apply)
        self.name_input.returnPressed.connect(self.do_apply)
        self.keep_area_box.toggled.connect(
            lambda _=False: self.show_target_slots(self.picked["option"])
        )
        cancel_btn.clicked.connect(self.dlg.reject)
        for keys, action in (
            ("Ctrl+Return", self.do_apply),
            ("Ctrl+Enter", self.do_apply),
            ("Ctrl+F", self.focus_search),
        ):
            QShortcut(QKeySequence(keys), self.dlg).activated.connect(action)

        self.show_details(None)
        self.show_target_slots(None)
        self.search_box.setFocus()
        start = next(
            (
                category.child(i)
                for category in self.category_items.values()
                for i in range(category.childCount())
                if (option := self.option_of(category.child(i))) is not None
                and option.name == pick
            ),
            None,
        )
        if pick and start is not None:
            self.tree.setCurrentItem(start)
            self.tree.scrollToItem(start)
        if self.cost:
            self.action_combo.setCurrentIndex(
                max(self.action_combo.findData(str(self.cost)), 0)
            )
        self.dlg.resize(self.dlg.width(), _effect_dialog_height(self.dlg))
        self.dlg.exec()
        if self.area_request:
            self.app._start_area_targeting(
                self.picked["option"], self.name_input.text().strip()
            )

    def lay_out_target_slots(self):
        while self.target_grid.count():
            self.target_grid.takeAt(0)
        cells = [row for row, _ in self.target_slots] + [
            self.add_target_btn,
            self.missing_lbl,
        ]
        for index, widget in enumerate(cells):
            self.target_grid.addWidget(
                widget,
                index // (_TARGETS_PER_LINE + 1),
                index % (_TARGETS_PER_LINE + 1),
            )

    def add_target_slot(self, char: dict | None) -> QComboBox:
        """A box picking `char` (None: nobody yet), with its × button."""
        row, layout = row_widget()
        layout.setSpacing(2)
        combo = QComboBox()
        combo.setObjectName("targetPick")
        combo.addItem(_NO_TARGET, -1)
        for index, choice in enumerate(self.choices):
            combo.addItem(f"{choice['name']}{self.app._distance_note(choice)}", index)
        if char is not None:
            at = next((i for i, c in enumerate(self.choices) if c is char), -1)
            combo.setCurrentIndex(max(combo.findData(at), 0))
        remove = QPushButton("×")
        remove.setObjectName("removeTarget")
        remove.setAutoDefault(False)
        remove.setFixedWidth(_TARGET_BUTTON_WIDTH)
        remove.setToolTip("Take this target away")
        layout.addWidget(combo, stretch=1)
        layout.addWidget(remove)
        slot = (row, combo)
        self.target_slots.append(slot)
        combo.currentIndexChanged.connect(lambda _=0: self.targets_changed())
        remove.clicked.connect(lambda _=False: self.remove_target_slot(slot))
        self.lay_out_target_slots()
        return combo

    def remove_target_slot(self, slot: tuple[QWidget, QComboBox]):
        """Take a box away; the last one empties instead."""
        if slot not in self.target_slots:
            return
        self.target_slots.remove(slot)
        slot[0].setParent(None)
        slot[0].deleteLater()
        if not self.target_slots:
            self.add_target_slot(None)
        self.lay_out_target_slots()
        self.targets_changed()

    def add_empty_target_slot(self):
        combo = self.add_target_slot(None)
        combo.setFocus()
        self.show_target_slots(self.picked["option"])

    def resisters(self) -> list[dict]:
        return [t for t in self.targets if legendary_resistances_left(t) > 0]

    def covered(self, target: dict, origin=None) -> dict:
        """Target with the map's cover against what's picked in it."""
        ignores = _ignores_cover(self.picked["option"])
        return self.app._covered(self.source, target, origin, ignores)

    def spell_range_text(self, target: dict) -> str:
        """ "past the spell's 60 ft. range" for a spell aimed at target
        from too far, on the map in use; "" for one aimed as an area
        (its point is what's checked, in the area bar)."""
        option = self.picked["option"]
        if self.aimed is not None or not self.app.arena_settings.in_use:
            return ""
        if option is None or option.area is not None:
            return ""
        warning = spell_range_warning(
            pick_spell_range_ft(option), self.source, target, self.app.arena_settings
        )
        return warning.split(" away, ", 1)[-1] if warning else ""

    def reach_of(self, target: dict) -> RangeCheck:
        """What the map says of the pick's range to target."""
        attack = pick_attack_range(self.picked["option"], self.source)
        return self.app._range_check(self.source, target, attack)

    def show_attack_info(self, target: dict):
        box = self.shield_boxes.get(id(target))
        wielding = None if box is None else box.isChecked()
        feet = self.app._attacker_distance_ft(self.source, target)
        reach = self.reach_of(target)
        info = self.attack_infos[id(target)]
        info.setText(
            _attack_text(
                self.source, target, wielding, feet, self.covered(target), reach
            )
        )
        info.setToolTip(
            _attack_tooltip(
                self.source,
                target,
                feet,
                self.app._map_cover(self.source, target).text,
                reach,
            )
        )

    def show_pick_rows(self):
        """The target rows again once a pick is made: its range and
        whether it ignores cover count in them."""
        for target in self.targets:
            if id(target) in self.attack_infos:
                self.show_attack_info(target)
        self.show_save_bonuses()

    def build_roll_rows(self):
        """The rows for the targets now picked, keeping what was typed
        (and each Shield box) for a target still picked."""
        typed = {
            **{("total", k): box.text() for k, box in self.typed_inputs.items()},
            **{("attack", k): box.text() for k, box in self.attack_inputs.items()},
            **{("extra", k): box.text() for k, (_, box) in self.extra_rows.items()},
        }
        wielded = {k: box.isChecked() for k, box in self.shield_boxes.items()}
        for widget in self.roll_rows.values():
            widget.setParent(None)
            widget.deleteLater()
        save_rows, totals, infos, _, _ = target_roll_rows(
            self.targets,
            "typedTotal",
            "The total with the save bonus already in it, like 14 or 9+5."
            " Blank rolls for them.",
        )
        # A hit's extra damage (Hunter's Mark) is a roll of its own: a box
        # more on its target's row, for what was rolled at the table.
        extra_boxes = {
            id(target): [
                (
                    (id(target), label),
                    f"{label[len(self.source['name']) + 3:]}: {extra_text(extra)}",
                    f"{label}: what was rolled at the table for its"
                    f" {extra_text(extra)}, its dice twice over on a Critical"
                    " Hit. Blank rolls it, unless the damage is a total typed"
                    " in, which has it already. 0 leaves it out.",
                )
                for label, extra in hit_extras(self.source, target)
            ]
            for target in self.targets
            if self.source is not None
        }
        # A target with a Shield can be wielding it or not: a box on its
        # row, its AC worked out by it.
        shield_checks = {
            id(target): (
                "Shield",
                f"Whether {target['name']} wields their Shield. The attack is"
                f" against AC {stored_armor(_with_shield(target, True))} with"
                f" it and {stored_armor(_with_shield(target, False))} without"
                " it (before effects and cover), and it stays as set here.",
                wielded.get(id(target), not is_shield_off(target)),
            )
            for target in self.targets
            if has_shield(target)
        }
        attack_rows, attacks, attack_labels, extras, shields = target_roll_rows(
            self.targets,
            "typedAttack",
            "The total with the bonus already in it, like 17 or 12+5, or"
            " nat 20 or nat 1. Blank rolls for the source.",
            extra_boxes,
            shield_checks,
        )
        for kept in (
            self.typed_inputs,
            self.save_infos,
            self.attack_inputs,
            self.attack_infos,
            self.extra_rows,
            self.shield_boxes,
        ):
            kept.clear()
        self.typed_inputs.update(totals)
        self.save_infos.update(infos)
        self.attack_inputs.update(attacks)
        self.attack_infos.update(attack_labels)
        self.extra_rows.update(extras)
        self.shield_boxes.update(shields)
        self.roll_rows.update(save=save_rows, attack=attack_rows)
        self.rolls_layout.addWidget(save_rows)
        self.rolls_layout.addWidget(attack_rows)
        for kind, boxes in (("total", totals), ("attack", attacks)):
            for key, box in boxes.items():
                box.setText(typed.get((kind, key), ""))
        for key, (_, box) in extras.items():
            box.setText(typed.get(("extra", key), ""))
        for box in [
            *totals.values(),
            *attacks.values(),
            *(box for _, box in extras.values()),
        ]:
            box.returnPressed.connect(lambda: self.do_apply())
        for target in self.targets:
            self.show_attack_info(target)
            if id(target) in self.shield_boxes:
                self.shield_boxes[id(target)].toggled.connect(
                    lambda _=False, t=target: self.show_attack_info(t)
                )
        self.resist_box.setToolTip(
            "Left: "
            + ", ".join(
                f"{t['name']} {legendary_resistances_left(t)}" for t in self.resisters()
            )
        )

    def amount_kind(self) -> str:
        return self.amount_combo.currentText()

    def show_amount_controls(self):
        """The box's title, hint and the damage-only controls, for what
        the amount is."""
        kind = self.amount_kind()
        is_damage = kind == DAMAGE_AMOUNT
        self.amount_header.setText(_AMOUNT_TITLES[kind])
        self.damage_input.setPlaceholderText(_AMOUNT_HINTS[kind])
        self.damage_input.setToolTip(
            "Dice are rolled once, for everyone it hits"
            if is_damage
            else "Dice are rolled once, for every target"
        )
        for widget in (self.type_combo, self.resistances_box):
            widget.setVisible(is_damage)

    def show_push(self, option: EffectOption | None):
        push = option.push if option is not None else None
        if push is None or not self.pushes_on_map or self.source is None:
            self.push_box.hide()
            return
        way = "toward" if push.toward else "away from"
        size = f" ({push.largest.value} or smaller)" if push.largest else ""
        self.push_box.setText(
            f"Who it lands on is {push.text} {way} {self.source['name']}{size}"
        )
        self.push_box.setChecked(True)
        self.push_box.show()

    def select_in_area(self):
        self.area_request.append(True)
        self.dlg.reject()

    def roll_kind(self) -> str:
        if self.roll_combo.currentText() == ATTACK_ROLL:
            return ATTACK_ROLL
        return SAVING_THROW if self.ability_combo.currentData() is not None else NO_ROLL

    def choose_kind(self, kind: str):
        self.roll_combo.setCurrentText(
            ATTACK_ROLL if kind == ATTACK_ROLL else SAVING_THROW
        )
        if kind == NO_ROLL:
            self.ability_combo.setCurrentIndex(0)
        elif kind == SAVING_THROW and self.ability_combo.currentData() is None:
            self.ability_combo.setCurrentIndex(
                max(self.ability_combo.findData(self.last_ability["value"]), 1)
            )
        self.show_roll_controls()

    def show_custom_row(self):
        for widget in self.custom_widgets:
            widget.setVisible(self.duration_combo.currentData() == "custom")

    def show_save_bonuses(self):
        ability = self.ability_combo.currentData()
        if ability is not None:
            self.last_ability["value"] = ability
        for target in self.targets:
            info = self.save_infos[id(target)]
            if ability is None:
                info.setText("")
                continue
            seen = self.covered(target, self.cover_origin)
            far = self.spell_range_text(target)
            info.setText(_save_text(seen, ability) + (f"; {far}" if far else ""))
            info.setToolTip(_save_tooltip(seen, ability))

    def show_roll_controls(self):
        kind = self.roll_kind()
        is_attack = kind == ATTACK_ROLL
        has_save = kind == SAVING_THROW
        for name, button in self.kind_buttons.items():
            button.setChecked(name == kind)
        self.save_line.setVisible(not is_attack)
        for widget in (self.dc_label, self.dc_input):
            widget.setVisible(has_save)
        self.attack_line.setVisible(is_attack)
        self.mode_chips.setVisible(kind != NO_ROLL)
        self.repeat_box.setVisible(has_save)
        # Hit Points aren't halved by a save: every target gets them.
        self.half_box.setVisible(has_save and self.amount_kind() == DAMAGE_AMOUNT)
        self.resist_box.setVisible(bool(self.resisters()) and has_save)
        self.rolls_hint.setVisible(kind != NO_ROLL)
        self.roll_rows["save"].setVisible(bool(self.typed_inputs) and has_save)
        self.roll_rows["attack"].setVisible(bool(self.attack_inputs) and is_attack)
        for row in self.extra_rows.values():
            for widget in row:
                widget.setVisible(self.amount_kind() == DAMAGE_AMOUNT)
        self.mode_combo.setEnabled(has_save or is_attack)
        for widget in (self.dc_input, self.half_box, self.repeat_box, self.resist_box):
            widget.setEnabled(has_save)
        for total_input in self.typed_inputs.values():
            total_input.setEnabled(has_save)
        self.condition_header.setText(
            {
                ATTACK_ROLL: "Condition (on a hit)",
                SAVING_THROW: "Condition (on a failed save)",
            }.get(kind, "Condition")
        )
        self.show_save_bonuses()

    def show_typed_type(self, text: str):
        if self.amount_kind() != DAMAGE_AMOUNT:
            return  # healing has no type
        try:
            parts = rolled_damage(_DICELESS.sub("1", text))
        except AmountError:
            return
        if parts[0][1] is not None:
            self.type_combo.setCurrentIndex(self.type_combo.findData(parts[0][1]))

    def show_preview(self):
        """What Apply will do, in a line, so a wrong pick shows before it
        lands. Nothing here is rolled."""
        kind = self.roll_kind()
        mode = self.mode_combo.currentText()
        with_mode = f" with {mode}" if kind != NO_ROLL and mode != "Neutral" else ""
        parts = []
        if kind == SAVING_THROW:
            parts.append(
                f"DC {self.dc_input.value()} {self.ability_combo.currentText()} save{with_mode}"
            )
        elif kind == ATTACK_ROLL:
            parts.append(f"Attack {self.bonus_input.value():+d} vs AC{with_mode}")
        amount = self.amount_kind()
        if amount == DAMAGE_AMOUNT:
            damage = _damage_preview(
                self.damage_input.text(), self.type_combo.currentData()
            )
            if damage and kind == SAVING_THROW:
                damage += (
                    ", half on a save"
                    if self.half_box.isChecked()
                    else ", none on a save"
                )
            if damage:
                parts.append(damage)
        elif self.damage_input.text().strip():
            parts.append(
                _amount_text(self.damage_input.text().strip(), amount) + " for all"
            )
        condition = self.name_combo.currentText().strip()
        if condition:
            lasts = self.duration_combo.currentText()
            if self.duration_combo.currentData() == "custom":
                lasts = f"{self.amount_input.value()} {self.unit_combo.currentText()}"
            if self.duration_combo.currentData() is not None:
                condition += f" ({lasts[0].lower()}{lasts[1:]})"
            if kind == SAVING_THROW and self.repeat_box.isChecked():
                condition += ", save ends"
            parts.append(condition)
        costs = []
        if self.caster is not None:
            if self.slot_combo.currentData() is not None:
                costs.append(self.slot_combo.currentText())
            if self.action_combo.currentData() is not None:
                costs.append(self.action_combo.currentText())
            if self.concentrate_box.isChecked():
                costs.append("concentration")
        if costs:
            parts.append("costs " + ", ".join(costs))
        if not parts:
            self.preview_lbl.setText(
                "Pick something on the left, or fill in a roll, damage,"
                " healing or a condition."
            )
            return
        on = (
            self.source_name
            if self.on_itself(self.picked["option"])
            else _count(len(self.targets), "target")
        )
        self.preview_lbl.setText(f"On {on}: " + " · ".join(parts))

    def on_itself(self, option: EffectOption | None) -> bool:
        """Whether the pick goes on its user alone, whoever is targeted
        (_apply_custom_effect: Second Wind)."""
        return option is not None and option.targets_self and self.source is not None

    def show_target_slots(self, option: EffectOption | None):
        """The target boxes for the pick: none for one that goes on its
        user, + only while it may target more, and "Target: missing"
        while it needs one and has none."""
        itself = self.on_itself(option)
        self.target_boxes.setVisible(not itself)
        self.itself_lbl.setVisible(itself)
        name = option.name if option is not None else ""
        if itself:
            self.itself_lbl.setText(f"itself ({name} goes on its user)")
        count = option.targets_at(self.slot_combo.currentData()) if option else None
        room = count is None or len(self.target_slots) < count
        self.add_target_btn.setEnabled(room)
        self.add_target_btn.setToolTip(
            "Add another target"
            if count is None or room
            else f"{name} may target {_count(count, 'creature')}"
        )
        keeps_area = self.aimed is not None and self.keep_area_box.isChecked()
        self.missing_lbl.setVisible(not itself and not self.targets and not keeps_area)
        if itself:
            self.apply_btn.setToolTip(f"Apply to {self.source_name} (Ctrl+Enter)")
        elif self.targets:
            self.apply_btn.setToolTip(
                f"Apply to {_count(len(self.targets), 'target')} (Ctrl+Enter)"
            )
        elif keeps_area:
            self.apply_btn.setToolTip(
                "Put the area on the map, with no targets (Ctrl+Enter)"
            )
        else:
            self.apply_btn.setToolTip("Pick a target first")

    def targets_changed(self):
        """The boxes' picks, in order and once each, are the targets; the
        rows per target follow them."""
        chosen: list[dict] = []
        for _, combo in self.target_slots:
            index = combo.currentData()
            if isinstance(index, int) and index >= 0:
                char = self.choices[index]
                if not any(char is c for c in chosen):
                    chosen.append(char)
        if [id(c) for c in chosen] != [id(t) for t in self.targets]:
            self.targets[:] = chosen
            self.build_roll_rows()
            self.show_roll_controls()
            self.show_target_count(self.picked["option"])
            self.show_preview()
        self.show_target_slots(self.picked["option"])

    # Each reads what's typed for every target, or says what's wrong
    # under the form and gives None (use_cast/form.py).
    def say(self, problem: str):
        self.problem_lbl.setText(problem)

    def typed_totals(self) -> dict[int, list[int | None]] | None:
        texts = {key: box.text() for key, box in self.typed_inputs.items()}
        times = self.times_input.value()
        return read_or_say(lambda: use_cast_form.typed_totals(texts, times), self.say)

    def typed_attacks(self) -> dict[int, list[AttackRoll | None]] | None:
        texts = {key: box.text() for key, box in self.attack_inputs.items()}
        times = self.times_input.value()
        return read_or_say(lambda: use_cast_form.typed_attacks(texts, times), self.say)

    def typed_extras(self) -> dict[int, dict[str, list[int | None]]] | None:
        texts = {key: box.text() for key, (_, box) in self.extra_rows.items()}
        times = self.times_input.value()
        return read_or_say(lambda: use_cast_form.typed_extras(texts, times), self.say)

    def typed_maximum(self) -> dict[int, int] | None:
        shown = self.maximum_input.isVisibleTo(self.dlg)
        text = self.maximum_input.text() if shown else ""
        keys = [id(t) for t in self.targets]
        return read_or_say(lambda: use_cast_form.typed_maximum(text, keys), self.say)

    def do_apply(self):
        if self.applied:
            return
        is_attack = self.roll_combo.currentText() == ATTACK_ROLL
        ability = None if is_attack else self.ability_combo.currentData()
        # "stunned" is Stunned, so the rules see it as they should; and
        # "Frightened + Incapacitated" is both.
        condition = CONDITION_JOINER.join(
            next((s for s in self.suggestions if s.lower() == typed.lower()), typed)
            for typed in condition_names(self.name_combo.currentText())
        )
        kind = self.amount_kind()
        damage: list[tuple[int, str]] = []
        hit_points = 0
        if kind == DAMAGE_AMOUNT:
            damage, problem = read_damage(
                self.damage_input.text(), self.type_combo.currentData()
            )
        else:
            hit_points, problem = read_hit_points(self.damage_input.text(), kind)
        if problem:
            self.problem_lbl.setText(problem)
            return
        pick: EffectOption | None = self.picked["option"]
        # A pick the source spends (a feature with no numbers) is enough.
        spends = pick is not None and pick.is_tracked and self.caster is not None
        ends = pick is not None and bool(pick.ends_conditions)
        # The Push mastery's row only moves its target.
        ends = ends or (pick is not None and pick.push is not None)
        keeps_area = self.aimed is not None and self.keep_area_box.isChecked()
        if not self.targets and not keeps_area and not self.on_itself(pick):
            self.problem_lbl.setText(
                "Target missing: pick one at the top, or keep the area on" " the map."
            )
            return
        if (
            not keeps_area
            and not is_attack
            and ability is None
            and not damage
            and not hit_points
            and not condition
            and not spends
            and not ends
        ):
            self.problem_lbl.setText(
                "Add a saving throw, damage, healing or a condition."
            )
            return
        totals = self.typed_totals() if ability is not None else {}
        attacks = self.typed_attacks() if is_attack else {}
        extras = self.typed_extras() if is_attack and kind == DAMAGE_AMOUNT else {}
        maximum = self.typed_maximum()
        if totals is None or attacks is None or extras is None or maximum is None:
            return
        self.typed_rolls.update(totals=totals, attacks=attacks, extras=extras)
        self.applied.append(True)
        duration = self.duration_combo.currentData()
        if duration == "custom":
            unit = CUSTOM_DURATION_UNITS[self.unit_combo.currentText()]
            duration = {"seconds": self.amount_input.value() * unit}
        self.app._custom_save = {
            "roll": self.roll_combo.currentText(),
            "ability": self.ability_combo.currentData(),
            "dc": self.dc_input.value(),
            "half": self.half_box.isChecked(),
            "bonus": self.bonus_input.value(),
            "source": self.source,
        }
        critical_damage = []
        if is_attack and kind == DAMAGE_AMOUNT:
            critical_damage, _ = read_damage(
                self.damage_input.text(), self.type_combo.currentData(), critical=True
            )
        effect = CustomEffect(
            name=self.name_input.text().strip(),
            condition=condition,
            duration=duration,
            notes=self.notes_input.text(),
            damage=damage,
            critical_damage=critical_damage,
            count_resistances=self.resistances_box.isChecked(),
            healing=hit_points if kind == HEALING else 0,
            temp_hp=hit_points if kind == TEMP_HP else 0,
            slot_level=(
                self.again_level
                if self.again is not None
                else self.slot_combo.currentData()
            ),
            action_cost=self.action_combo.currentData(),
            concentration=self.concentrate_box.isChecked(),
            from_area=self.kept_area if self.again is not None else "",
            attack_bonus=self.bonus_input.value() if is_attack else None,
            typed_attacks=use_cast_form.nth(attacks, 0),
            typed_extras=use_cast_form.nth(extras, 0),
            ability=ability,
            dc=self.dc_input.value(),
            mode=self.mode_combo.currentText(),
            half_on_save=self.half_box.isChecked(),
            use_legendary_resistance=self.resist_box.isChecked(),
            repeat_save=self.repeat_box.isChecked(),
            typed_totals=use_cast_form.nth(totals, 0),
            typed_hit_point_maximum=maximum,
            shields=(
                {key: box.isChecked() for key, box in self.shield_boxes.items()}
                if is_attack
                else {}
            ),
            pick=pick,
            weapon_attack=pick.weapon_attack if pick is not None else None,
            # A total with no dice, not the pick's own damage, was rolled
            # at the table: a hit's extra damage isn't added to it.
            typed_damage=bool(damage)
            and not _DICELESS.search(self.damage_input.text())
            and self.damage_input.text() != self.picked["damage"],
            area=(
                _with_slot(self.aimed["record"], self.slot_combo.currentData())
                if self.aimed is not None and keeps_area
                else None
            ),
            cover_origin=self.cover_origin,
            push=(
                pick.push
                if pick is not None
                and not self.push_box.isHidden()
                and self.push_box.isChecked()
                else None
            ),
        )
        # The boxes' picks become the targets, as if clicked on the cards.
        if [id(t) for t in self.targets] != [id(t) for t in self.app.target_characters]:
            self.app._set_targets(list(self.targets))
        times = self.times_input.value()
        if times == 1:
            self.app._apply_custom_effect(effect)
        else:
            copies = use_cast_form.repeated(
                effect,
                times,
                amount_text=self.damage_input.text(),
                damage_type=self.type_combo.currentData(),
                kind=self.amount_kind(),
                typed_rolls=self.typed_rolls,
            )
            self.app._apply_custom_effects(copies)
        self.dlg.accept()

    def show_details(self, option: EffectOption | None):
        self.details.setHtml(
            _option_details(option) if option is not None else _DETAILS_HINT
        )

    def show_duration(self, seconds: int | None, until: tuple[str, str] | None):
        """Select a pick's duration: a turn, a time, or until removed. A
        turn of a source that isn't there falls back to until removed."""
        index = 0
        if until is not None:
            wanted_turn = {"until": until[0], "of": until[1]}
            index = next(
                (
                    i
                    for i in range(self.duration_combo.count())
                    if self.duration_combo.itemData(i) == wanted_turn
                ),
                0,
            )
        elif seconds:
            wanted = {"seconds": seconds}
            index = next(
                (
                    i
                    for i in range(self.duration_combo.count())
                    if self.duration_combo.itemData(i) == wanted
                ),
                -1,
            )
            fit = custom_duration(seconds) if index < 0 else None
            if fit is not None:
                self.amount_input.setValue(fit[0])
                self.unit_combo.setCurrentText(fit[1])
                index = self.duration_combo.findData("custom")
        self.duration_combo.setCurrentIndex(max(index, 0))

    def fill_from(self, option: EffectOption):
        """Replace everything a pick says with what this one does, and
        clear what it doesn't say. A None DC or bonus keeps the dialog's."""
        self.picked["option"] = None  # so the slot below isn't taken for an edit
        self.name_input.setText(option.name)
        self.note_lbl.setText(option.note)
        self.note_lbl.setVisible(bool(option.note))
        self.roll_combo.setCurrentText(option.roll)
        self.ability_combo.setCurrentIndex(
            max(self.ability_combo.findData(option.ability), 0) if option.ability else 0
        )
        if option.dc is not None:
            self.dc_input.setValue(option.dc)
        if option.bonus is not None:
            self.bonus_input.setValue(option.bonus)
        self.half_box.setChecked(option.half_on_save)
        self.repeat_box.setChecked(option.repeat_save)
        # What the source doesn't have (no slot left, no source) is "No ...".
        # findData never finds a PactSlot, and == alone can't tell one
        # from a spell slot of its level.
        self.slot_combo.setCurrentIndex(
            next(
                (
                    index
                    for index in range(self.slot_combo.count())
                    if self.slot_combo.itemData(index) == option.slot_level
                    and type(self.slot_combo.itemData(index)) is type(option.slot_level)
                ),
                0,
            )
            if self.again is None
            else 0
        )
        spends = self.cost or option.action_cost
        if self.again is not None:
            spends = None  # a kept area acting: its cast was spent
        action_index = self.action_combo.findData(str(spends))
        self.action_combo.setCurrentIndex(max(action_index, 0) if spends else 0)
        self.concentrate_box.setChecked(option.concentration and self.again is None)
        # A type left from before would disagree with the pick's damage.
        self.type_combo.setCurrentIndex(0)
        self.amount_combo.setCurrentText(option.amount_kind)
        level = (
            self.again_level
            if self.again is not None
            else self.slot_combo.currentData()
        )
        damage = option.damage_at(level)
        self.damage_input.setText(damage)
        times = option.instances_at(level)
        self.times_input.setValue(times)
        self.name_combo.setCurrentText(option.condition)
        self.notes_input.clear()
        self.show_duration(option.duration_seconds, option.until)
        self.problem_lbl.setText("")
        self.show_details(option)
        self.show_target_count(option)
        self.show_maximum_box(option)
        self.show_push(option)
        self.picked.update(
            option=option, damage=damage, times=times, search=self.search_box.text()
        )
        self.show_pick_rows()

    def drop_pick(self, name: str):
        """Typing another name makes it the GM's own effect: nothing is
        spent for the pick, and the slot box no longer upcasts it."""
        option = self.picked["option"]
        if option is None or name == option.name:
            return
        self.picked["option"] = None
        self.tree.clearSelection()
        self.note_lbl.setText("")
        self.note_lbl.hide()
        self.show_details(None)
        self.show_target_count(None)
        self.show_maximum_box(None)
        self.show_push(None)
        self.show_pick_rows()

    def show_maximum_box(self, option: EffectOption | None):
        """The Hit Point maximum box, for a pick whose badge rolls one."""
        dice = [
            m.amount
            for _, modifiers in (option.badge_modifiers if option else ())
            for m in modifiers
            if isinstance(m, HitPointMaximum) and "d" in m.amount + m.upcast
        ]
        self.maximum_input.clear()
        self.maximum_input.setPlaceholderText(
            f"Hit Point maximum ({dice[0]}) rolled, or blank to roll" if dice else ""
        )
        self.maximum_input.setVisible(bool(dice))

    def show_target_count(self, option: EffectOption | None):
        """How many creatures the pick may target at the slot chosen
        ("Targets: 4 at level 2" for Bless), and when more are targeted,
        how many too many. It warns; the GM can still apply it."""
        self.show_target_slots(option)
        slot = self.slot_combo.currentData()
        count = option.targets_at(slot) if option is not None else None
        if option is None or count is None:
            self.target_count_lbl.hide()
            return
        at = f" at level {int(slot)}" if option.target_upcast and slot else ""
        text = f"Targets: {count}{at}"
        if len(self.targets) > count:
            text += (
                f" ({len(self.targets)} targeted: {len(self.targets) - count} too many)"
            )
        self.target_count_lbl.setText(text)
        self.target_count_lbl.show()

    def upcast(self):
        """A pick's damage and times at the slot now chosen, unless they've
        been edited."""
        option = self.picked["option"]
        self.show_target_count(option)
        if option is None:
            return
        if self.times_input.value() == self.picked["times"]:
            self.picked["times"] = option.instances_at(self.slot_combo.currentData())
            self.times_input.setValue(self.picked["times"])
        if self.damage_input.text() != self.picked["damage"]:
            return
        damage = option.damage_at(self.slot_combo.currentData())
        self.damage_input.setText(damage)
        self.picked["damage"] = damage

    def option_of(self, item: QTreeWidgetItem | None) -> EffectOption | None:
        """What a row offers: nothing for a category or a greyed row."""
        if item is None or item.isHidden() or item.isDisabled():
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)

    def on_selection_changed(self):
        items = self.tree.selectedItems()
        option = self.option_of(items[0]) if items else None
        if option is not None:
            self.fill_from(option)

    def on_current_changed(self, item: QTreeWidgetItem | None):
        """A greyed row can't be picked, but its rules text can be read."""
        if item is not None and item.isDisabled():
            self.show_details(item.data(0, Qt.ItemDataRole.UserRole))

    def first_pickable(self) -> QTreeWidgetItem | None:
        match = first_visible_item(self.category_items)
        if match is None or not match.isDisabled():
            return match
        for category in self.category_items.values():
            for i in range(category.childCount()):
                if self.option_of(category.child(i)) is not None:
                    return category.child(i)
        return None

    def search_entered(self):
        """Enter picks the top match, and then applies what's picked. Once
        the search has changed since the pick, it picks the top match again."""
        current = self.tree.currentItem()
        option = self.option_of(current)
        searched = self.search_box.text() == self.picked["search"]
        if option is not None and option is self.picked["option"] and searched:
            self.do_apply()
            return
        match = self.first_pickable()
        if match is None:
            return
        again = self.option_of(match)
        if match is current and again is not None:
            self.fill_from(again)  # no selection change to do it
        else:
            self.tree.setCurrentItem(match)

    def item_activated(self, item: QTreeWidgetItem):
        option = self.option_of(item)
        if option is None:
            return
        if self.picked["option"] is not option:
            self.fill_from(option)
        self.do_apply()

    def focus_search(self):
        self.search_box.setFocus()
        self.search_box.selectAll()
