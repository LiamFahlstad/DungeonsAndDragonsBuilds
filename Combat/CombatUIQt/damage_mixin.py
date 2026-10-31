"""Damage/healing mixin for CombatAppQt."""

import random

from Combat.Definitions import Action
from Core.Definitions import Condition
from .amounts import AmountError, parse_amount, parse_damage
from .stats import _default_stats, damage_dealt_key, damage_taken_key
from Core.Rules import ability_modifier
from .state import CombatWindowState
from .undo import undoable

# A Concentration save's DC: half the damage taken, between these.
MIN_CONCENTRATION_DC = 10
MAX_CONCENTRATION_DC = 30


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

        if has_type(target.get("damage_immunities")):
            return 0, "immune"
        resisted = has_type(target.get("damage_resistances"))
        vulnerable = has_type(target.get("damage_vulnerabilities"))
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
        max_hp = char.get("max_hp", 1)
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

    @undoable
    def _do_apply_damage(self, check_resistance: bool):
        parts = self._damage_parts()
        if parts is None:
            return
        source = self.selected_character or self._current_turn_character()

        for target in list(self.target_characters):
            saved = any(target is s for s in self._saved_targets)
            taken = 0
            knockout = False
            for amount, damage_type in parts:
                dmg, downed = self._damage_target(
                    target, amount, damage_type, source, check_resistance, saved
                )
                taken += dmg
                knockout = knockout or downed

            # A creature that makes Death Saving Throws falls Unconscious at
            # 0 HP (which also ends its Concentration); any other one dies.
            if knockout and self._char_death_state(target) != "dead":
                self._add_condition_to(target, Condition.UNCONSCIOUS.value)

            if "Concentrating" in target.get("conditions", []):
                if knockout:
                    self._remove_condition_from(target, "Concentrating", source=target)
                elif taken > 0 and self.settings.ask_concentration_saves:
                    # Only damage taken forces a save (damage soaked by
                    # temporary HP still counts); 0 after immunity doesn't.
                    self._ask_concentration_save(target, taken)

        if source is not None:
            source["_last_damage_type"] = parts[-1][1]
        if self.settings.reset_damage_type_after_hit:
            self._show_source_damage_type(source)
        self.damage_input.clear()
        self._saved_targets = []
        self._update_target_label()
        for target in self.target_characters:
            self._rebuild_card(target)

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
        self._log_event(
            f"{target['name']} takes {dmg} {damage_type} damage{source_suffix}{outcome_suffix}",
            character=target["name"],
            action=Action.DAMAGE,
            value=damage_value,
        )

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
        saving_throws = char.get("Saving Throws") or {}
        for key in ("CONSTITUTION", "Con", "CON"):
            if key in saving_throws:
                return saving_throws[key]
        ability_scores = char.get("Ability Scores") or {}
        for key in ("Con", "CON", "CONSTITUTION"):
            if key in ability_scores:
                return ability_modifier(ability_scores[key])
        return 0

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
        roll = random.randint(1, 20) + self._con_save_mod(char)
        self._settle_concentration(char, dc, roll >= dc, roll)

    @undoable
    def _settle_concentration(
        self, char: dict, dc: int, kept: bool, roll: int | None = None
    ):
        """The result of a Concentration save asked for on char's card."""
        checks = char.get("concentration_checks", [])
        if dc in checks:
            checks.remove(dc)
        if not checks:
            char.pop("concentration_checks", None)
        name = char["name"]
        result = f"DC {dc}, rolled {roll}" if roll is not None else f"DC {dc}"
        if kept:
            self._log_event(f"{name} keeps concentration ({result})", character=name)
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
        source_name = source["name"] if source is not None else None

        dead = []
        for char in list(self.target_characters):
            death_state = self._char_death_state(char)
            # A dead creature can't regain Hit Points until it is revived
            # (the card's Revive button).
            if death_state == "dead":
                dead.append(char["name"])
                continue
            was_downed = death_state != "alive"

            pre_hp = char["hp"]
            char["hp"] = min(char["hp"] + heal, char["max_hp"])
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

            self._rebuild_card(char)
        if dead:
            names = ", ".join(dead)
            self._show_status(f"Not healed: {names} is dead. Use Revive on the card.")
        if len(dead) < len(self.target_characters):
            self.heal_input.clear()

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
        source_name = source["name"] if source is not None else None

        for target in list(self.target_characters):
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
