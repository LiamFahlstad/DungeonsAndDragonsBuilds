"""Damage/healing mixin for CombatAppQt."""

from Combat.Arena.cover import (
    CoverReading,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.ranges import (
    AttackRange,
    RangeCheck,
)
from Combat.Definitions import Action
from Combat.Effects.always_on import KEEPS_CONCENTRATION
from Combat.Effects.modifiers import (
    extra_text,
    hit_extras,
)
from Combat.Effects.triggers import (
    AttackOutcome,
    DropOutcome,
    PendingAttack,
    TriggerMode,
    reduced_damage,
)
from Combat.Effects.sight import Seen
from Core.Definitions import Condition
from Combat.Fight.amounts import AmountError, parse_amount, parse_damage
from Combat.Fight.attacks import resolve_attack_roll, use_up_badges
from Combat.Fight.health import (
    DEAD,
    DYING,
    death_state,
    fail_death_save,
    revive,
    succeed_death_save,
)
from Combat.Fight.damage import (
    damage_after_defenses,
    bloodied_outcomes,
    damage_type_modifier,
    deal_damage,
)
from Combat.Fight.effects_given import grant_temp_hp
from Combat.Fight.attack_rolls import (
    AttackRoll,
    armor_in_use,
    parse_attack_roll,
)
from Combat.Fight.saves import CustomEffect, roll_save, save_modifier
from Combat.Fight.cascade import apply_bloodied, heal_target, note_health_change
from Combat.Fight.step import Step
from .state import CombatWindowState
from .steps import run_step, show_step
from .undo import undoable

# A Concentration save's DC: half the damage taken, between these.
MIN_CONCENTRATION_DC = 10
MAX_CONCENTRATION_DC = 30


class DamageMixin(CombatWindowState):
    """Mixin for damage and healing related methods."""

    def _amount_for_targets(self, text: str) -> int | None:
        """What was typed in an amount field if it can be applied now: there's
        a target and it's a number. Otherwise says why not and returns None."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return None
        amount = parse_amount(text)
        if amount is None:
            shown = f"'{text.strip()}' isn't an amount" if text.strip() else "no amount"
            self._show_status(f"Nothing applied: {shown}. Type a total, like 7 or 4+3.")
        return amount

    def _damage_type_modifier(self, target: dict, dmg: int, damage_type: str):
        """(the damage, its outcome) after target's defenses: see
        Combat/Fight/damage.py's damage_type_modifier."""
        return damage_type_modifier(target, dmg, damage_type)

    def _apply_bloodied_condition(self, char: dict, source: dict | None = None):
        """Bloodied given or taken off by char's Hit Points, logged from
        `source`, or silently without one (replay): Combat/Fight/cascade.py's
        apply_bloodied."""
        run_step(self, apply_bloodied, char, source)

    def _apply_damage(self):
        """Apply damage as-is, with no resistance/vulnerability/immunity checks."""
        self._do_apply_damage(check_resistance=False)

    def _apply_damage_checked(self):
        """Apply damage after checking the target's resistances/vulnerabilities/immunities
        against the selected damage type."""
        self._do_apply_damage(check_resistance=True)

    def _damage_parts(self) -> list[tuple[int, str]] | None:
        """The Damage field as (amount, damage type) to apply, a type left out
        being the one showing in the dropdown. Otherwise says why not."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return None
        try:
            parts = parse_damage(self.damage_input.text())
        except AmountError as error:
            self._show_status(f"Nothing applied: {error}. Try 12, 4+3 or 12 fire.")
            return None
        chosen = self.damage_type_combo.currentData()
        typed = [(amount, damage_type or chosen) for amount, damage_type in parts]
        if any(damage_type is None for _, damage_type in typed):
            self._show_status("Nothing applied: pick a damage type, or type 12 fire.")
            return None
        return typed

    def _check_attack_roll(self) -> tuple[list[dict], str] | None:
        """Check the Attack roll field against each target. Returns the targets
        it hit, including any with no AC to check, and how it went against the
        AC, for the status line, or None if there's nothing to check, after
        saying why."""
        if not self.target_characters:
            self._show_status("Nothing applied: right-click a card to pick a target.")
            return None
        text = self.attack_roll_input.text().strip()
        roll = parse_attack_roll(text)
        if roll is None:
            shown = f"'{text}' isn't an attack roll" if text else "no attack roll"
            self._show_status(f"Nothing applied: {shown}. Try 17, 12+5 or nat 20.")
            return None

        source = self.selected_character or self._current_turn_character()
        hit_targets = []
        results = []
        for target in self.target_characters:
            hit, result = self._resolve_attack_roll(target, roll, source)
            if hit is not False:
                hit_targets.append(target)
                # A typed total gets none of a hit's extra damage (Decision 4),
                # so say what to add at the table (Q27).
                critical = roll.is_critical or self._critical_against(source, target)
                twice = ", its dice twice" if critical else ""
                result += "".join(
                    f"; {extra_text(extra)} ({label}){twice}"
                    for label, extra in hit_extras(source, target)
                )
            results.append(result)
        self.attack_roll_input.clear()
        return hit_targets, "; ".join(results)

    def _attacker_distance_ft(
        self, attacker: dict | None, target: dict | None
    ) -> int | None:
        """Fight.distance_ft (Combat/Fight/fight.py)."""
        return self.fight.distance_ft(attacker, target)

    def _sees(self, viewer: dict | None, other: dict | None) -> Seen:
        """Fight.sees (Combat/Fight/fight.py)."""
        return self.fight.sees(viewer, other)

    def _sees_of(self, viewer: dict, other: dict) -> bool | None:
        """_sees's answer alone, for the triggers' "you can see it"."""
        return self._sees(viewer, other).can

    def _map_cover(
        self,
        source: dict | None,
        target: dict | None,
        origin: list[Cell] | None = None,
    ) -> CoverReading:
        """Fight.map_cover (Combat/Fight/fight.py)."""
        return self.fight.map_cover(source, target, origin)

    def _covered(
        self,
        source: dict | None,
        target: dict,
        origin: list[Cell] | None = None,
        ignores_cover: bool = False,
    ) -> dict:
        """Fight.covered (Combat/Fight/fight.py)."""
        return self.fight.covered(source, target, origin, ignores_cover)

    def _range_check(
        self, source: dict | None, target: dict | None, attack: AttackRange | None
    ) -> RangeCheck:
        """Fight.range_check (Combat/Fight/fight.py)."""
        return self.fight.range_check(source, target, attack)

    def _cover_warning(self, source: dict | None, target: dict) -> str:
        """Fight.cover_warning (Combat/Fight/fight.py)."""
        return self.fight.cover_warning(source, target)

    def _critical_against(self, attacker: dict | None, target: dict | None) -> bool:
        """Fight.critical_against (Combat/Fight/fight.py)."""
        return self.fight.critical_against(attacker, target)

    def _resolve_attack_roll(
        self,
        target: dict,
        roll: AttackRoll,
        source: dict | None,
        notes: tuple[str, ...] = (),
        ignores_cover: bool = False,
    ) -> tuple[bool | None, str]:
        """Check `roll` against target's AC and log how it went:
        Combat/Fight/attacks.py's resolve_attack_roll."""
        return run_step(
            self, resolve_attack_roll, target, roll, source, notes, ignores_cover
        )

    def _use_up_badges(self, attacker: dict | None, target: dict | None):
        """End the badges an attack roll by attacker against target has used
        up: Combat/Fight/attacks.py's use_up_badges, each taken off through
        the @undoable _remove_condition_from, as before: a monster's action
        button rolls with no undo step open, and taking one off is a step."""
        run_step(
            self, use_up_badges, attacker, target, remove=self._remove_condition_from
        )

    @undoable
    def _apply_attack_roll(self):
        """Enter in the Attack roll field: a hit goes on to its damage, for the
        targets it hit, and a miss leaves the field empty for the next roll.
        The Damage field's Enter deals it as this roll's hit, while this is
        the last step (what the hit triggers needs it); a miss triggers what
        comes with one now."""
        roll = parse_attack_roll(self.attack_roll_input.text().strip())
        targets = list(self.target_characters)
        checked = self._check_attack_roll()
        if checked is None:
            return
        hit_targets, results = checked
        source = self.selected_character or self._current_turn_character()
        self._checked_attack = None
        if source is not None and roll is not None:
            self._checked_attack = PendingAttack(
                source,
                roll.is_critical,
                targets=tuple(hit_targets),
                step=self._open_undo_point,
                total=roll.total,
            )
            with self._one_trigger_prompt():
                for target in targets:
                    if not any(target is t for t in hit_targets):
                        self._after_attack(
                            AttackOutcome(source, target, False, damage_dealt=0)
                        )
        self._show_status(results)
        if hit_targets:
            self._set_targets(hit_targets)
            self._focus_damage_input()

    def _pending_attack(self, source: dict | None) -> PendingAttack | None:
        """The attack whose damage the Damage field now holds, rolled in the
        step before by source: the Attack roll field's (while that's still
        the last step), or a monster's action button's (while its roll is
        still in the field, which an undo clears). Each is used once."""
        checked, rolled = self._checked_attack, self._rolled_attack
        self._checked_attack = None
        self._rolled_attack = None
        if source is None:
            return None
        if (
            checked is not None
            and checked.attacker is source
            and checked.step is not None
            and self.history
            and self.history[-1] is checked.step
        ):
            return checked
        if (
            rolled is not None
            and rolled.attacker is source
            and self._rolled_damage_text
        ):
            return rolled
        return None

    @undoable
    def _do_apply_damage(self, check_resistance: bool):
        parts = self._damage_parts()
        if parts is None:
            return
        targets = list(self.target_characters)
        source = self.selected_character or self._current_turn_character()
        results = ""
        # The attack this damage is the hit of, if it's known to be one: the
        # roll typed in the Attack roll field, or one rolled the step before.
        attack: PendingAttack | None = None
        misses: list[dict] = []
        if self.attack_roll_input.text().strip():
            roll = parse_attack_roll(self.attack_roll_input.text().strip())
            checked = self._check_attack_roll()
            if checked is None:
                return
            hit_targets, results = checked
            misses = [t for t in targets if not any(t is h for h in hit_targets)]
            targets = hit_targets
            self._checked_attack = self._rolled_attack = None
            if source is not None and roll is not None:
                attack = PendingAttack(source, roll.is_critical, total=roll.total)
            if not targets:
                with self._one_trigger_prompt():
                    self._after_misses(attack, misses)
                # The roll's used up, so applying again deals it: some damage
                # lands on a miss, like the Graze mastery's.
                self._show_status(
                    f"{results}, so no damage applied."
                    " Apply again to deal it anyway."
                )
                return
        else:
            attack = self._pending_attack(source)
            if attack is not None and attack.targets is not None:
                # Only the targets the roll hit are its hits.
                if not all(any(t is h for h in attack.targets) for t in targets):
                    attack = None

        # What the hits and the damage trigger is asked about once, at the
        # end: the attacker's riders, the targets' Hellish Rebuke.
        with self._one_trigger_prompt():
            self._deal_typed_damage(
                targets, parts, source, check_resistance, attack, misses, results
            )

    def _deal_typed_damage(
        self,
        targets: list[dict],
        parts: list[tuple[int, str]],
        source: dict | None,
        check_resistance: bool,
        attack: PendingAttack | None,
        misses: list[dict],
        results: str,
    ):
        """The Damage field's damage on each of `targets`. When it's an
        attack's hit, each target first answers it (_before_hit: Shield may
        make it a miss, Deflect Attacks takes some off), and what the hit
        triggers comes after."""
        hits: list[tuple[dict, int, bool]] = []
        for target in targets:
            saved = any(target is s for s in self._saved_targets)
            these = parts
            # A Critical Hit by the roll, or by what the target has
            # (Paralyzed's, from within 5 feet on the map).
            critical = attack is not None and (
                attack.critical or self._critical_against(attack.attacker, target)
            )
            if attack is not None:
                still, reduction = self._before_hit(
                    AttackOutcome(
                        attack.attacker,
                        target,
                        True,
                        critical=critical,
                        kind=attack.kind,
                        row=attack.row,
                        total=attack.total,
                        armor=armor_in_use(self._covered(attack.attacker, target)),
                    )
                )
                if not still:
                    misses = [*misses, target]
                    results = "; ".join(
                        part
                        for part in (results, f"{target['name']}: then a miss")
                        if part
                    )
                    continue
                these = reduced_damage(parts, reduction)
            dealt = (
                self._deal_damage(
                    target,
                    these,
                    source,
                    check_resistance,
                    saved,
                    critical=critical,
                )
                if these
                else 0
            )
            hits.append((target, dealt, critical))

        if source is not None:
            # The first part: the hit's own type, not an extra added after
            # it ("3 Piercing + 4 Force" from Hunter's Mark-like riders).
            source["_last_damage_type"] = parts[0][1]
        if self.settings.reset_damage_type_after_hit:
            self._show_source_damage_type(source)
        self.damage_input.clear()
        self._saved_targets = []
        self._update_target_label()
        for target in self.target_characters:
            self._rebuild_card(target)
        if results:  # last, as logging the damage clears the status line
            self._show_status(results)
        if attack is not None:
            self._after_misses(attack, misses)
            for target, damage, critical in hits:
                if any(target is c for c in self.characters):
                    self._after_attack(
                        AttackOutcome(
                            attack.attacker,
                            target,
                            True,
                            critical=critical,
                            kind=attack.kind,
                            row=attack.row,
                            damage_dealt=damage,
                        )
                    )
                    # PendingAttack (Combat/Effects) can't name CustomEffect
                    # while it lives here in the UI, so its rider is typed
                    # object (combat-ui-refactor-plan step 5 moves it down).
                    if isinstance(attack.rider, CustomEffect):
                        # A monster's action button: what its hit gives
                        # (Molten Strike's Prone), as its picker row does.
                        self._give_effect_conditions(target, attack.rider)
                        self._rebuild_card(target)

    def _after_misses(self, attack: PendingAttack | None, misses: list[dict]):
        """What the misses of an attack typed in trigger."""
        if attack is None:
            return
        for target in misses:
            self._after_attack(
                AttackOutcome(attack.attacker, target, False, damage_dealt=0)
            )

    def _deal_damage(
        self,
        target: dict,
        parts: list[tuple[int, str]],
        source: dict | None,
        check_resistance: bool,
        saved: bool,
        critical: bool = False,
    ) -> int:
        """One hit on target, of each (amount, damage type) in parts
        (Combat/Fight/damage.py's deal_damage), then what it leaves the
        window: the Concentration save asked, what the hit triggers, and
        what the status line says of what it dropped to instead of 0.
        Returns the damage it took, after Resistance and Immunity. If it
        would drop target to 0 Hit Points, target is asked first about what
        it can drop to instead (_drops_to_instead: Relentless Endurance);
        if it does, the hit leaves it there, and it isn't knocked out."""
        state_before = self._char_death_state(target)
        drops_to, notes = self._drops_to_instead(
            target, parts, source, check_resistance, saved
        )
        step = Step(self.fight, self.logger, self.asker)
        dealt = deal_damage(
            step,
            target,
            parts,
            source,
            check_resistance,
            saved,
            critical=critical,
            state_before=state_before,
            drops_to=drops_to,
            ask_concentration=self.settings.ask_concentration_saves,
        )
        show_step(self, step.result)
        if dealt.concentration_save:
            self._ask_concentration_save(target, dealt.taken)
        for outcome in (*dealt.outcomes, *bloodied_outcomes(dealt, target, source)):
            self._after_attack(outcome)
        if notes:
            # After the damage, whose log lines cleared the status line.
            status = self._status_label.text()
            self._show_status("; ".join(part for part in (status, *notes) if part))
        return dealt.taken

    def _drops_to_instead(
        self,
        target: dict,
        parts: list[tuple[int, str]],
        source: dict | None,
        check_resistance: bool,
        saved: bool,
    ) -> tuple[int, list[str]]:
        """The Hit Points target drops to instead of 0, if `parts` would drop
        it there and it uses something that says so (DROPS_TO_ZERO: Relentless
        Endurance's 1): applied by itself when nothing's to decide, otherwise
        asked now, in a pop-up of its own, before any of the damage is dealt;
        what it spends is spent inside the hit's undo step. 0 when nothing
        is used. With the setting ask_triggers off, it's a turn-column button
        instead (picked late, it brings target back up), and target drops.
        Also what the status line should say of it once the damage is dealt
        ("Relentless Endurance: no uses left")."""
        if target["hp"] <= 0:
            return 0, []
        damage = sum(
            damage_after_defenses(target, amount, kind, check_resistance, saved)
            for amount, kind in parts
        )
        past_temp = damage - min(target.get("temp_hp", 0), damage)
        if past_temp < target["hp"]:
            return 0, []
        found, spent = self._drop_firings(
            DropOutcome(target, source, damage, past_temp - target["hp"])
        )
        notes = list(spent)
        drops_to = 0
        if found:
            used = []
            for firing in found:
                if firing.mode is TriggerMode.AUTO and self._use_trigger(firing, notes):
                    used.append(firing)
            asks = [f for f in found if f.mode is TriggerMode.ASK]
            if asks and not self.settings.ask_triggers:
                self._hit_prompts = (*self._hit_prompts, *asks)
                self._refresh_turn_prompts()
            elif asks and not used:
                used += [firing for firing, _ in self._answer_firings(asks, notes)]
            drops_to = max((f.row.drops_to for f in used), default=0)
        return drops_to, notes

    def _note_health(self, char: dict):
        """Note what the change of HP that's just over showed the players, and
        save the fight state: cascade.py's note_health_change."""
        run_step(self, note_health_change, char)

    def _show_source_damage_type(self, source: dict | None):
        """Show the damage type source last dealt, or a blank one, so a type
        left over from another source can't go on this one's hit unnoticed."""
        remembered = None
        if source is not None and self.settings.remember_damage_type:
            remembered = source.get("_last_damage_type")
        index = self.damage_type_combo.findData(remembered)
        self.damage_type_combo.setCurrentIndex(max(index, 0))

    def _show_typed_damage_type(self, text: str):
        """Show a damage type as it's typed in the Damage field."""
        try:
            parts = parse_damage(text)
        except AmountError:
            return
        if parts[0][1] is not None:
            index = self.damage_type_combo.findData(parts[0][1])
            self.damage_type_combo.setCurrentIndex(index)

    def _toggle_saved(self, char: dict):
        """Mark or unmark one target as having saved, for half damage."""
        if any(char is s for s in self._saved_targets):
            self._saved_targets = [s for s in self._saved_targets if s is not char]
        else:
            self._saved_targets = self._saved_targets + [char]
        self._update_target_label()
        self._rebuild_card(char)

    def _toggle_saved_for_all(self):
        """The ½ Saved button: every target saved, or none did."""
        everyone = len(self._saved_targets) == len(self.target_characters)
        self._saved_targets = [] if everyone else list(self.target_characters)
        self._update_target_label()
        for target in self.target_characters:
            self._rebuild_card(target)

    def _con_save_mod(self, char: dict) -> int:
        """Return the CON saving throw modifier for a character."""
        return save_modifier(char, "CON")

    def _ask_concentration_save(self, char: dict, dmg: int):
        """Ask for the Constitution save that dmg forces: on char's card, or
        rolled here for a monster with the setting on."""
        dc = min(MAX_CONCENTRATION_DC, max(MIN_CONCENTRATION_DC, dmg // 2))
        if self.settings.monsters_roll_concentration and not char.get("_is_player"):
            self._roll_concentration(char, dc)
            return
        char.setdefault("concentration_checks", []).append(dc)
        self._write_log(self._read_log())  # a continued fight still owes it
        self._rebuild_card(char)

    @undoable
    def _roll_concentration(self, char: dict, dc: int):
        """A monster's Concentration save, a Constitution saving throw: its
        modifiers count as in any save rolled here (Bless's 1d4, a mode),
        and the log says how."""
        result = roll_save(
            char,
            "CON",
            dc,
            "Neutral",
            one_die_if_straight=True,
            against=KEEPS_CONCENTRATION,
        )
        self._settle_concentration(char, dc, result.success, result.total, result.note)

    @undoable
    def _settle_concentration(
        self,
        char: dict,
        dc: int,
        kept: bool,
        roll: int | None = None,
        note: str = "",
    ):
        """The result of a Concentration save asked for on char's card, with
        `note` on how it was rolled, if it was rolled here."""
        checks = char.get("concentration_checks", [])
        if dc in checks:
            checks.remove(dc)
        if not checks:
            char.pop("concentration_checks", None)
        name = char["name"]
        result = f"DC {dc}, rolled {roll}" if roll is not None else f"DC {dc}"
        if note:
            result = f"{result}, {note}"
        if kept:
            self._log_event(
                f"{name} keeps concentration ({result})",
                character=name,
                value={"condition": "Concentrating"},
            )
            self._rebuild_card(char)
            return
        char.pop("concentration_checks", None)
        if "Concentrating" in char.get("conditions", []):
            char["conditions"].remove("Concentrating")
            self._end_concentration_spells(char)
        # Concentration is always lost by the caster's own failed save,
        # so the caster is both source and target here.
        cond_value = {
            "condition": "Concentrating",
            "source_name": name,
            "target_name": name,
        }
        self._log_event(
            f"{name} loses concentration ({result})",
            character=name,
            action=Action.REMOVE_CONDITION,
            value=cond_value,
        )
        self._rebuild_card(char)

    @undoable
    def _apply_heal(self):
        heal = self._amount_for_targets(self.heal_input.text())
        if heal is None:
            return

        source = self.selected_character or self._current_turn_character()
        dead = [
            char["name"]
            for char in list(self.target_characters)
            if not self._heal_target(char, heal, source)
        ]
        if dead:
            names = ", ".join(dead)
            self._show_status(f"Not healed: {names} is dead. Use Revive on the card.")
        if len(dead) < len(self.target_characters):
            self.heal_input.clear()

    def _heal_target(self, char: dict, heal: int, source: dict | None) -> bool:
        """char regains `heal` Hit Points from source, logged; False for a dead
        creature. Heal and the Custom Effect dialog share it: cascade.py's
        heal_target."""
        return run_step(self, heal_target, char, heal, source)

    @undoable
    def _revive(self, char: dict):
        """Bring a dead creature back with 1 HP, as Revivify or Raise Dead
        would; healing alone can't (see _apply_heal)."""
        if death_state(char) != DEAD:
            return
        self._select_character(char)
        revive(char)
        self._log_event(
            f"{char['name']} is revived with 1 HP",
            character=char["name"],
            action=Action.REVIVE,
            value={"hp": 1, "target_name": char["name"]},
        )
        self._remove_condition_from(char, Condition.UNCONSCIOUS.value)
        self._apply_bloodied_condition(char)
        self._rebuild_card(char)

    @undoable
    def _apply_failed_death_save(self, char: dict):
        if death_state(char) != DYING:
            return
        self._select_character(char)
        newly_dead = fail_death_save(char)
        if newly_dead:
            self._log_event(
                f"{char['name']} has died (3 failed death saves)",
                character=char["name"],
                action=Action.DEATH_SAVE_FAIL,
                value=newly_dead,
            )
        else:
            self._log_event(
                f"{char['name']} fails a death save "
                f"({char['death_saves_fail']}/3 fails)",
                character=char["name"],
                action=Action.DEATH_SAVE_FAIL,
                value=newly_dead,
            )
        if newly_dead and "Concentrating" in char.get("conditions", []):
            self._remove_condition_from(char, "Concentrating", source=char)
        if newly_dead:
            self._summons_die_with(char)
        self._refresh_selected_card()

    @undoable
    def _apply_success_death_save(self, char: dict):
        if death_state(char) != DYING:
            return
        self._select_character(char)
        if succeed_death_save(char):
            self._log_event(
                f"{char['name']} stabilizes (3 successful death saves)",
                character=char["name"],
                action=Action.DEATH_SAVE_SUCCESS,
                value=None,
            )
        else:
            self._log_event(
                f"{char['name']} succeeds a death save "
                f"({char['death_saves_success']}/3 successes)",
                character=char["name"],
                action=Action.DEATH_SAVE_SUCCESS,
                value=None,
            )
        self._refresh_selected_card()

    @undoable
    def _apply_temp_hp(self):
        amount = self._amount_for_targets(self.temp_hp_input.text())
        if amount is None:
            return

        source = self.selected_character or self._current_turn_character()
        for target in list(self.target_characters):
            self._give_temp_hp(target, amount, source)

    def _give_temp_hp(self, target: dict, amount: int, source: dict | None):
        """Give target `amount` temporary Hit Points from source:
        Combat/Fight/effects_given.py's grant_temp_hp."""
        run_step(self, grant_temp_hp, target, amount, source)
