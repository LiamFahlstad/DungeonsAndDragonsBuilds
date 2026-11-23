"""Conditions mixin for CombatAppQt."""

from dataclasses import replace
from html import escape

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QHeaderView,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
)

from Combat.Arena.arena import (
    DASHES_KEY,
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
from Combat.Arena.lasting import AREA_KEY, find_area
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
    note_origin,
    repeat_saves,
    set_duration,
    set_repeat_save,
    tick,
)
from Combat.Effects.modifiers import (
    attack_plan,
    has_condition,
    hit_plan,
    hit_point_maximum,
    hit_point_maximum_notes,
    loses_dodge,
    rolled_modifiers,
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
from Core.Definitions import Condition
from Model.Content.CombatModifiers import AttackKind, HitPointMaximum
from Model.Content.StandardActions import DASH, DODGE, HIDDEN
from Combat.Fight.attack_rolls import (
    armor_in_use,
    has_shield,
    is_shield_off,
    SHIELD_OFF,
)
from Combat.Fight.effect_options import (
    COLLAPSED_CATEGORIES,
    effect_options,
    pick_attack_range,
    regained_uses,
    triggered_rows,
)
from .features_mixin import FEATURE_BADGE_COLOR
from Combat.Fight.monster_actions import legendary_resistances_left, roll_dice
from .player_view import note_condition_immunity
from Combat.Fight.resources import feature_lack, monster_action_lack, spell_slot_lack
from Combat.Fight.saves import (
    ABILITIES,
    ATTACK_ROLL,
    DAMAGE_AMOUNT,
    DEFAULT_SAVE_DC,
    FEATURE,
    HEALING,
    SPELL,
    STANDARD_ACTION,
    TEMP_HP,
    CustomEffect,
    EffectOption,
    is_immune_to,
    read_damage,
    read_hit_points,
    roll_extra_damage,
    roll_planned_attack,
    roll_save,
    with_extra_damage,
)
from .spells_mixin import spell_badge_color, spell_badge_description
from Combat.Fight.conditions import gain_condition, incapacitates, lose_condition
from .state import CombatWindowState
from .tree_filter import filter_category_tree
from .undo import undoable
from .use_cast.dialog import (
    UseCastDialog,
    _SUMMARY_COLOR,
    _ignores_cover,
    _where_from,
)

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


_SUMMARY_WIDTH = 150  # a picker row's numbers ("+6  1d8 + 4 Slashing")
# A row the source is out of (spent, too few legendary actions left).
_UNAVAILABLE_COLOR = "#6a6a7a"
# How long a concentration effect runs with no time on it: the longest there is
# in general use, for the GM to end by hand or by losing concentration.
LONGEST_CONCENTRATION = 60 * 60


def _option_tooltip(option: EffectOption) -> str:
    """A picker row's tooltip: what the row says, then its rules text. Rich
    text, so Qt wraps it."""
    text = escape(option.tooltip, quote=False).replace("\n", "<br>")
    where = _where_from(option)
    source = f"<i>{where}</i><br>" if where else ""
    return f"<b>{escape(option.row_text, quote=False)}</b><br>{source}{text}"


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
        # Who grapples it, the condition and the statistics:
        # Combat/Fight/conditions.py's gain_condition.
        if gain_condition(char, cond, source, counted=counted):
            source_name = source["name"] if source is not None else None
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
        # Its lasting effect, a Dash's movement and who grappled it go with
        # it: Combat/Fight/conditions.py's lose_condition.
        lost = lose_condition(char, cond)
        if lost is not None:
            stands_for, emptied = lost.stands_for, lost.emptied
            # What it did to the Hit Point maximum (Aid) goes with it.
            if hit_point_maximum(char) != lost.maximum_before:
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
        UseCastDialog(self).run(pick, cost, kept_area)

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
