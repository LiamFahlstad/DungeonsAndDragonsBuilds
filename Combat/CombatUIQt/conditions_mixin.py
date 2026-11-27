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

from Combat.Definitions import (
    CombatStatus,
    Phase,
)
from Combat.Effects.active_effects import (
    ActiveEffect,
    active_effects,
    drop_repeat_save,
    repeat_saves,
    tick,
)
from Combat.Effects.modifiers import attack_plan
from Combat.Effects.triggers import (
    AttackOutcome,
    FailedSaveOutcome,
    UsesOutcome,
    outcome_firings,
)
from Model.Content.CombatModifiers import AttackKind
from Combat.Fight.attack_rolls import armor_in_use
from Combat.Fight.attacks import apply_reduction
from Combat.Fight.effect_options import (
    COLLAPSED_CATEGORIES,
    effect_options,
    pick_attack_range,
    triggered_rows,
)
from Combat.Fight.effects_given import (
    add_custom_condition,
    give_badge_modifiers,
    give_effect_condition,
    give_effect_conditions,
    hold_concentration,
    hold_given,
    is_later_step,
    regain_feature_uses,
    set_shield,
    with_hit_extras,
)
from Combat.Fight.monster_actions import legendary_resistances_left
from Combat.Fight.picked import option_duration, picked_effect
from Combat.Fight.resources import effect_lacks, use_pick
from Combat.Fight.saves import (
    ABILITIES,
    SPELL,
    CustomEffect,
    EffectOption,
    evades,
    roll_effect_save,
    roll_planned_attack,
    roll_repeat_save,
)
from Combat.Fight.cascade import (
    add_condition,
    keep_hit_points_in_maximum,
    remove_condition,
    spend_action,
)
from .state import CombatWindowState
from .steps import run_step
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
        duration=option_duration(option),
        pick=option,
    )


_SUMMARY_WIDTH = 150  # a picker row's numbers ("+6  1d8 + 4 Slashing")
# A row the source is out of (spent, too few legendary actions left).
_UNAVAILABLE_COLOR = "#6a6a7a"


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
        """char gets `cond` from `source`, logged, and what that sets off:
        Combat/Fight/cascade.py's add_condition."""
        run_step(self, add_condition, char, cond, source, counted=counted)

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
        """char's badge `name` gives `modifiers` while it's on:
        Combat/Fight/effects_given.py's give_badge_modifiers."""
        run_step(
            self,
            give_badge_modifiers,
            char,
            name,
            modifiers,
            levels_up=levels_up,
            source=source,
            rolled_maximum=rolled_maximum,
        )

    def _keep_hit_points_in_maximum(self, char: dict, reason: str):
        """char has no more Hit Points than its maximum, now that `reason`
        changed it: cascade.py's keep_hit_points_in_maximum."""
        run_step(self, keep_hit_points_in_maximum, char, reason)

    @undoable
    def _remove_condition_from(self, char: dict, cond: str, source: dict | None = None):
        """char loses `cond`, logged, and what that sets off:
        Combat/Fight/cascade.py's remove_condition."""
        run_step(self, remove_condition, char, cond, source)

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
        """Give every target (or those of `targets`) `cond`, attributed to
        the source: effects_given.py's add_custom_condition."""
        targets = self.target_characters if targets is None else targets
        source = self.selected_character or self._current_turn_character()
        run_step(self, add_custom_condition, cond, duration, notes, targets, source)

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
                    damage = apply_reduction(damage, reduction)
            if effect.ability is not None:
                saved = self._roll_effect_save(target, effect, source)
                results.append(saved)
            avoided, halved = self._save_damage(target, effect, saved, bool(damage))
            dealt = 0
            if damage and not avoided:
                dealt = self._deal_damage(
                    target,
                    damage,
                    source,
                    effect.count_resistances,
                    halved,
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
        elif effect.from_area or is_later_step(effect):
            self._hold_with_area(effect, applied, caster)
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
        """A hit's damage with the extra damage that comes with it:
        effects_given.py's with_hit_extras."""
        return run_step(self, with_hit_extras, source, target, damage, effect, critical)

    def _set_shield(self, char: dict, wielding: bool | None):
        """char wields its Shield or sets it down: effects_given.py's
        set_shield."""
        run_step(self, set_shield, char, wielding)

    @undoable
    def _apply_custom_effects(self, effects: list[CustomEffect]):
        """Several Custom dialog effects as one step (the rays of one
        Scorching Ray): undone together, and what their hits trigger asked
        about once (Q41)."""
        with self._one_trigger_prompt():
            for effect in effects:
                self._apply_custom_effect(effect)

    def _apply_row(
        self, owner: dict, target: dict, option: EffectOption, answers: object = None
    ) -> bool:
        """Use one picker row of owner's on target, as picking it in the
        Custom Effect dialog and applying it as it's filled in would: what
        it costs (a use, logged), its roll, damage and conditions. What a
        hit triggers comes this way (TurnPanelMixin._use_trigger), with the
        hit it `answers` (picked.py: a Critical Hit's dice twice). Returns
        whether it was applied: not if owner is out of what it spends (no
        uses left, the action used), which the caller says."""
        effect = picked_effect(option, self._custom_save, answers, owner)
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
        """char regains the uses option gives back: effects_given.py's
        regain_feature_uses."""
        run_step(self, regain_feature_uses, char, option)

    def _use_pick(self, caster: dict, effect: CustomEffect) -> bool | None:
        """What the dialog's pick was, used by caster: Combat/Fight/
        resources.py's use_pick."""
        return run_step(self, use_pick, caster, effect)

    def _effect_lacks(self, caster: dict, effect: CustomEffect) -> list[str | None]:
        """What caster is out of that the effect spends: resources.py's
        effect_lacks."""
        return effect_lacks(self.phase, caster, effect)

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
        """Caster's concentration on the effect: effects_given.py's
        hold_concentration."""
        run_step(self, hold_concentration, caster, label, effect, applied)

    def _hold_with_area(
        self, effect: CustomEffect, applied: list[dict], caster: dict | None
    ):
        """What a kept area or a later step of a casting gave, held by its
        spell's concentration: effects_given.py's hold_given."""
        run_step(self, hold_given, effect, applied, caster)

    def _give_effect_conditions(self, target: dict, effect: CustomEffect) -> list[dict]:
        """Give target what of effect lands: effects_given.py's
        give_effect_conditions."""
        source = self.selected_character or self._current_turn_character()
        return run_step(self, give_effect_conditions, target, effect, source)

    def _give_effect_condition(
        self, target: dict, effect: CustomEffect, condition: str
    ) -> bool:
        """Give target one of the effect's conditions: effects_given.py's
        give_effect_condition."""
        source = self.selected_character or self._current_turn_character()
        return run_step(self, give_effect_condition, target, effect, condition, source)

    def _save_damage(
        self, target: dict, effect: CustomEffect, saved: bool, has_damage: bool
    ) -> tuple[bool, bool]:
        """Whether effect's damage misses target after its save (`saved`),
        and whether it's halved: none on a success with half_on_save off;
        with Evasion (saves.evades), none on a success and half on a
        failure, which the log says."""
        avoided = effect.ability is not None and saved and not effect.half_on_save
        if not (has_damage and evades(target, effect)):
            return avoided, saved
        said = "no" if saved else "half"
        self._log_event(
            f"{target['name']}'s Evasion: {said} damage", character=target["name"]
        )
        return saved, True

    def _roll_effect_save(
        self, target: dict, effect: CustomEffect, source: dict | None = None
    ) -> bool:
        """Target's save against the effect, logged. Legendary Resistance turns
        a failure into a success, if the dialog said to use it. The map's
        cover counts in a Dexterity save: from source, or from the area's
        point of origin (effect.cover_origin)."""
        assert effect.ability is not None  # the caller checks
        name = target["name"]
        covered = self._covered(
            source, target, effect.cover_origin, _ignores_cover(effect.pick)
        )
        result = roll_effect_save(covered, effect, effect.typed_totals.get(id(target)))
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
                again = roll_effect_save(failed.char, effect)
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
        # With what its allies' auras give it (Aura of Protection).
        result = roll_repeat_save(self.fight.with_auras(char), effect, rolls.get(turn))
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
        # A spent Reaction's other Opportunity Attack buttons go (arena step
        # 23), and the selected card shows what's left: steps.py's show_step.
        run_step(self, spend_action, char, action_type)

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
