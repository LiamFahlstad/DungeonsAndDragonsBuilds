"""Damage/healing mixin for CombatAppQt."""

from Combat.Definitions import Action
from Combat.Effects.modifiers import (
    hit_notes,
    hit_point_maximum,
    immune_to_damage,
    resists,
    vulnerable_to,
)
from Combat.Effects.triggers import AttackOutcome, PendingAttack
from Combat.Summons import vanishes_at_zero_hp
from Core.Definitions import Condition
from .amounts import AmountError, parse_amount, parse_damage
from .attack_rolls import (
    AttackRoll,
    armor_bonus,
    cover_bonus,
    note_attack_roll,
    parse_attack_roll,
)
from .monster_actions import first_number
from .player_view import _player_names, _seen, note_damage_defense, note_health
from .saves import roll_save, save_modifier
from .stats import _default_stats, damage_dealt_key, damage_taken_key
from .state import CombatWindowState
from .undo import undoable

# A Concentration save's DC: half the damage taken, between these.
MIN_CONCENTRATION_DC = 10
MAX_CONCENTRATION_DC = 30
# How an attack roll went, as the log says it; None is no AC to check against.
_VERDICTS: dict[bool | None, str] = {
    True: "hits",
    False: "misses",
    None: "can't be checked against",
}


def _damage_type_value(t) -> str:
    return t.value if hasattr(t, "value") else str(t)


def _entry_damage_types(entry) -> list:
    if isinstance(entry, dict):
        return entry.get("damage_types", [])
    return getattr(entry, "damage_types", [])


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
        """Check target's damage immunities/resistances/vulnerabilities against
        damage_type and return (applied_dmg, outcome), outcome being one of
        'immune', 'resisted', 'vulnerable', 'resisted and vulnerable', or None.
        Immunity zeroes the damage; otherwise Resistance halves it (rounded
        down) and then Vulnerability doubles it, so both can apply."""

        def has_type(entries) -> bool:
            for entry in entries or []:
                if any(
                    _damage_type_value(t) == damage_type
                    for t in _entry_damage_types(entry)
                ):
                    return True
            return False

        # A condition or a badge can give these too (Petrified's Resistance
        # to all damage, Stoneskin's, Heroes' Feast's Poison).
        if has_type(target.get("damage_immunities")) or immune_to_damage(
            target, damage_type
        ):
            return 0, "immune"
        resisted = has_type(target.get("damage_resistances")) or resists(
            target, damage_type
        )
        vulnerable = has_type(target.get("damage_vulnerabilities")) or vulnerable_to(
            target, damage_type
        )
        if resisted:
            dmg //= 2
        if vulnerable:
            dmg *= 2
        if resisted and vulnerable:
            return dmg, "resisted and vulnerable"
        if resisted:
            return dmg, "resisted"
        if vulnerable:
            return dmg, "vulnerable"
        return dmg, None

    def _apply_bloodied_condition(self, char: dict, source: dict | None = None):
        """Auto-apply/remove Bloodied condition based on HP threshold. Pass
        `source` (the damage dealer/healer) to log the change with a source,
        same as any other condition; omit it for silent resyncs (replay)."""
        max_hp = hit_point_maximum(char) if "max_hp" in char else 1
        hp = char.get("hp", 0)
        is_bloodied = "Bloodied" in char.get("conditions", [])
        should_be_bloodied = hp > 0 and hp <= max_hp / 2

        if should_be_bloodied and not is_bloodied:
            if source is not None:
                self._add_condition_to(char, "Bloodied", source=source)
            else:
                char["conditions"].append("Bloodied")
        elif not should_be_bloodied and is_bloodied:
            if source is not None:
                self._remove_condition_from(char, "Bloodied", source=source)
            else:
                char["conditions"].remove("Bloodied")

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
            results.append(result)
        self.attack_roll_input.clear()
        return hit_targets, "; ".join(results)

    def _resolve_attack_roll(
        self,
        target: dict,
        roll: AttackRoll,
        source: dict | None,
        notes: tuple[str, ...] = (),
    ) -> tuple[bool | None, str]:
        """Check `roll` against target's AC, with its cover and modifiers, and
        log how it went, with `notes` on how it was rolled (attack_plan's) and
        what the GM should check about a hit. Returns whether it hit, None
        with no AC to check, and how it went against the AC, for the status
        line. The log doesn't say the AC, as the Limited view's players read
        it too. They don't learn from a hidden attacker's roll, which they
        never saw."""
        armor = first_number(target.get("ac"))
        bonus = armor_bonus(target)
        hit = roll.hits(None if armor is None else armor + bonus)
        # A player's summon is seen as its owner is, even while Invisible.
        if source is None or _seen(source, _player_names(self.characters)):
            note_attack_roll(target, roll, hit, bonus)
        if hit is not False:
            notes = (*notes, *hit_notes(target))
        name = target["name"]
        attacker = f"{source['name']}'s attack roll" if source else "Attack roll"
        critical = " (critical hit)" if roll.is_critical else ""
        noted = f", {', '.join(notes)}" if notes else ""
        self._log_event(
            f"{attacker} of {roll.text} {_VERDICTS[hit]} {name}{critical}{noted}",
            character=name,
        )
        why = f" ({'; '.join(notes)})" if notes else ""
        if armor is None:
            return hit, f"{name} has no AC to check{why}"
        cover = " with cover" if cover_bonus(target) else ""
        faced = f"AC {armor + bonus}{cover}"
        word = "hit" if hit else "miss"
        return hit, f"{name}: {roll.text} vs {faced}, {word}{why}"

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
                attack = PendingAttack(source, roll.is_critical)
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

        dealt = []
        for target in targets:
            saved = any(target is s for s in self._saved_targets)
            dealt.append(
                self._deal_damage(target, parts, source, check_resistance, saved)
            )

        if source is not None:
            source["_last_damage_type"] = parts[-1][1]
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
            with self._one_trigger_prompt():
                self._after_misses(attack, misses)
                for target, damage in zip(targets, dealt):
                    if any(target is c for c in self.characters):
                        self._after_attack(
                            AttackOutcome(
                                attack.attacker,
                                target,
                                True,
                                critical=attack.critical,
                                kind=attack.kind,
                                row=attack.row,
                                damage_dealt=damage,
                            )
                        )

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
    ) -> int:
        """One hit on target, of each (amount, damage type) in parts, and what
        the hit does to it: falling Unconscious, a Concentration save.
        Returns the damage it took, after Resistance and Immunity."""
        taken = 0
        knockout = False
        for amount, damage_type in parts:
            dmg, downed = self._damage_target(
                target, amount, damage_type, source, check_resistance, saved
            )
            taken += dmg
            knockout = knockout or downed
        self._note_health(target)
        # A summon whose spec says so vanishes at 0 HP (a drake), once
        # what it was concentrating on has ended.
        vanishes = knockout and vanishes_at_zero_hp(target)

        # A creature that makes Death Saving Throws falls Unconscious at
        # 0 HP (which also ends its Concentration); any other one dies.
        if knockout and not vanishes and self._char_death_state(target) != "dead":
            self._add_condition_to(target, Condition.UNCONSCIOUS.value)

        if "Concentrating" in target.get("conditions", []):
            if knockout:
                self._remove_condition_from(target, "Concentrating", source=target)
            elif taken > 0 and self.settings.ask_concentration_saves:
                # Only damage taken forces a save (damage soaked by
                # temporary HP still counts); 0 after immunity doesn't.
                self._ask_concentration_save(target, taken)
        if vanishes:
            self._vanish_at_zero_hp(target)
        return taken

    def _note_health(self, char: dict):
        """Note what the change of HP that's just over showed the players. The
        log was written before it was done, and a continued fight needs it."""
        note_health(char)
        self._write_log(self._read_log())

    def _damage_target(
        self,
        target: dict,
        amount: int,
        damage_type: str,
        source: dict | None,
        check_resistance: bool,
        saved: bool,
    ) -> tuple[int, bool]:
        """Deal one damage type to target, halved first if it saved. Returns
        (the damage dealt, whether it took target to 0 HP)."""
        source_name = source["name"] if source is not None else None
        dmg = amount // 2 if saved else amount
        outcome = None
        if check_resistance:
            dmg, outcome = self._damage_type_modifier(target, dmg, damage_type)
        defense = outcome
        if saved:
            outcome = f"saved, {outcome}" if outcome else "saved"

        pre_hp = target["hp"]
        pre_temp = target["temp_hp"]

        temp_reduction = min(target["temp_hp"], dmg)
        target["temp_hp"] -= temp_reduction
        # Hit Points can't go below 0.
        target["hp"] = max(0, target["hp"] - (dmg - temp_reduction))

        hp_delta = target["hp"] - pre_hp
        temp_delta = target["temp_hp"] - pre_temp

        knockout = pre_hp > 0 and target["hp"] <= 0

        target.setdefault("stats", _default_stats())
        target["stats"]["damage_taken"] = target["stats"].get("damage_taken", 0) + dmg
        taken_type_key = damage_taken_key(damage_type)
        target["stats"][taken_type_key] = target["stats"].get(taken_type_key, 0) + dmg
        if knockout:
            target["stats"]["times_downed"] = target["stats"].get("times_downed", 0) + 1

        if source is not None:
            source.setdefault("stats", _default_stats())
            source["stats"]["damage_dealt"] = (
                source["stats"].get("damage_dealt", 0) + dmg
            )
            type_key = damage_dealt_key(damage_type)
            source["stats"][type_key] = source["stats"].get(type_key, 0) + dmg
            if knockout:
                source["stats"]["knockouts"] = source["stats"].get("knockouts", 0) + 1

        damage_value = {
            "hp_delta": hp_delta,
            "temp_delta": temp_delta,
            "dmg": dmg,
            "damage_type": damage_type,
            "source_name": source_name,
            "target_name": target["name"],
            "knockout": knockout,
            "outcome": outcome,
        }
        source_suffix = f" from {source_name}" if source_name else ""
        outcome_suffix = f" ({outcome})" if outcome else ""
        readable = self._log_event(
            f"{target['name']} takes {dmg} {damage_type} damage{source_suffix}{outcome_suffix}",
            character=target["name"],
            action=Action.DAMAGE,
            value=damage_value,
        )
        if readable:
            note_damage_defense(target, damage_type, defense)

        # Auto-apply bloodied condition, attributed to whoever dealt the damage
        self._apply_bloodied_condition(target, source=source)

        self._rebuild_card(target)
        return dmg, knockout

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
        result = roll_save(char, "CON", dc, "Neutral", one_die_if_straight=True)
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
        """char regains `heal` Hit Points from source, up to its maximum,
        counted in both their stats and logged; one at 0 HP comes to. Returns
        False for a dead creature, which can't regain Hit Points until it's
        revived (the card's Revive button). Heal and the Custom Effect dialog
        share it."""
        death_state = self._char_death_state(char)
        if death_state == "dead":
            return False
        was_downed = death_state != "alive"
        source_name = source["name"] if source is not None else None

        pre_hp = char["hp"]
        char["hp"] = min(char["hp"] + heal, hit_point_maximum(char))
        actual_heal = char["hp"] - pre_hp

        char.setdefault("stats", _default_stats())
        char["stats"]["healing_received"] = (
            char["stats"].get("healing_received", 0) + actual_heal
        )
        if source is not None:
            source.setdefault("stats", _default_stats())
            source["stats"]["healing_done"] = (
                source["stats"].get("healing_done", 0) + actual_heal
            )

        heal_value = {
            "heal": actual_heal,
            "source_name": source_name,
            "target_name": char["name"],
        }

        source_suffix = f" from {source_name}" if source_name else ""

        if was_downed and char["hp"] > 0:
            char["death_saves_fail"] = 0
            char["death_saves_success"] = 0
            self._log_event(
                f"{char['name']} regains consciousness with {char['hp']} HP{source_suffix}",
                character=char["name"],
                action=Action.HEAL,
                value=heal_value,
            )
            # Regaining any Hit Points ends the Unconscious from 0 HP.
            self._remove_condition_from(char, Condition.UNCONSCIOUS.value)
        else:
            self._log_event(
                f"{char['name']} heals {actual_heal} HP{source_suffix}",
                character=char["name"],
                action=Action.HEAL,
                value=heal_value,
            )

        # Auto-apply bloodied condition, attributed to whoever healed
        self._apply_bloodied_condition(char, source=source)
        self._note_health(char)

        self._rebuild_card(char)
        return True

    @undoable
    def _revive(self, char: dict):
        """Bring a dead creature back with 1 HP, as Revivify or Raise Dead
        would; healing alone can't (see _apply_heal)."""
        if self._char_death_state(char) != "dead":
            return
        self._select_character(char)
        char["hp"] = 1
        char["death_saves_fail"] = 0
        char["death_saves_success"] = 0
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
        if self._char_death_state(char) != "dying":
            return
        self._select_character(char)
        pre_fail = char.get("death_saves_fail", 0)
        char["death_saves_fail"] = min(pre_fail + 1, 3)
        newly_dead = pre_fail < 3 and char["death_saves_fail"] >= 3
        if newly_dead:
            char.setdefault("stats", _default_stats())
            char["stats"]["deaths"] = char["stats"].get("deaths", 0) + 1
        if char["death_saves_fail"] >= 3:
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
        if self._char_death_state(char) != "dying":
            return
        self._select_character(char)
        char["death_saves_success"] = min(char.get("death_saves_success", 0) + 1, 3)
        if char["death_saves_success"] >= 3:
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
        """Give target `amount` temporary Hit Points from source, counted in
        both their stats and logged. Temp HP and Wild Shape share it."""
        source_name = source["name"] if source is not None else None
        old = target.get("temp_hp", 0)
        # Temporary Hit Points don't stack: keep the higher amount.
        target["temp_hp"] = max(old, amount)

        target.setdefault("stats", _default_stats())
        target["stats"]["temp_hp_received"] = (
            target["stats"].get("temp_hp_received", 0) + amount
        )
        if source is not None:
            source.setdefault("stats", _default_stats())
            source["stats"]["temp_hp_granted"] = (
                source["stats"].get("temp_hp_granted", 0) + amount
            )

        temp_hp_value = {
            "amount": amount,
            "source_name": source_name,
            "target_name": target["name"],
        }

        source_suffix = f" from {source_name}" if source_name else ""
        if amount > old:
            text = f"{target['name']} gains {amount} temp HP{source_suffix}"
            if old:
                text += f" (replacing {old})"
        else:
            text = (
                f"{target['name']} keeps {old} temp HP instead of "
                f"{amount}{source_suffix} (they don't stack)"
            )
        self._log_event(
            text,
            character=target["name"],
            action=Action.ADD_TEMP_HP,
            value=temp_hp_value,
        )
        self._rebuild_card(target)
