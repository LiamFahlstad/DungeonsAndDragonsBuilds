"""Damage on a combatant, Qt-free (Notes/combat-ui-refactor-plan.md, step
5.3, damage): what its Immunity, Resistance and Vulnerability make of an
amount, and what taking it does to its Hit Points and the fight's
statistics; and one hit dealt, logged, with what it sets off (R45): Bloodied,
falling Unconscious, failed Death Saving Throws at 0 Hit Points, a summon
vanishing, a Concentration save owed. What it asks first (what the target
drops to instead of 0) and what it triggers after are the window's
(DamageMixin._deal_damage), as the triggers still go through its Use / Cast
apply path."""

from dataclasses import dataclass, field

from Combat.Definitions import Action
from Combat.Effects.modifiers import immune_to_damage, resists, vulnerable_to
from Combat.Effects.triggers import (
    BloodiedOutcome,
    DamageOutcome,
    KnockoutOutcome,
    Outcome,
)
from Combat.Summons import vanishes_at_zero_hp
from Core.Definitions import Condition
from Model.Content.CombatModifiers import EndEvent

from .cascade import (
    add_condition,
    apply_bloodied,
    end_when,
    note_health_change,
    remove_condition,
)
from .health import damage_at_zero_hp, death_state
from .player_knowledge import note_damage_defense
from .stats import _default_stats, damage_dealt_key, damage_taken_key
from .step import Step
from .summons import summons_die_with, vanish_at_zero_hp


def _damage_type_value(t) -> str:
    return t.value if hasattr(t, "value") else str(t)


def _entry_damage_types(entry) -> list:
    if isinstance(entry, dict):
        return entry.get("damage_types", [])
    return getattr(entry, "damage_types", [])


def damage_type_modifier(target: dict, dmg: int, damage_type: str):
    """Check target's damage immunities/resistances/vulnerabilities against
    damage_type and return (applied_dmg, outcome), outcome being one of
    'immune', 'resisted', 'vulnerable', 'resisted and vulnerable', or None.
    Immunity zeroes the damage; otherwise Resistance halves it (rounded
    down) and then Vulnerability doubles it, so both can apply."""

    def has_type(entries) -> bool:
        for entry in entries or []:
            if any(
                _damage_type_value(t) == damage_type for t in _entry_damage_types(entry)
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


def damage_after_defenses(
    target: dict,
    amount: int,
    damage_type: str,
    check_resistance: bool,
    saved: bool,
) -> int:
    """What one damage type of a hit comes to on target: halved first if it
    saved, then its Immunity, Resistance and Vulnerability."""
    dmg = amount // 2 if saved else amount
    if check_resistance:
        dmg, _ = damage_type_modifier(target, dmg, damage_type)
    return dmg


@dataclass(frozen=True)
class DamageTaken:
    """What taking damage did: the damage, the change to Hit Points and to
    Temporary Hit Points, and whether it took the target to 0 Hit Points."""

    dmg: int
    hp_delta: int
    temp_delta: int
    knockout: bool


def take_damage(
    target: dict, dmg: int, damage_type: str, source: dict | None, floor: int = 0
) -> DamageTaken:
    """target takes `dmg` of `damage_type` (already through its defenses):
    its Temporary Hit Points first, and its Hit Points no lower than `floor`
    (what it drops to instead of 0: Relentless Endurance's 1). The target's
    damage taken and the source's damage dealt count it, and a knockout
    counts for both."""
    pre_hp = target["hp"]
    pre_temp = target["temp_hp"]

    temp_reduction = min(target["temp_hp"], dmg)
    target["temp_hp"] -= temp_reduction
    # Hit Points can't go below 0, nor below what it drops to instead.
    target["hp"] = max(floor, target["hp"] - (dmg - temp_reduction))

    knockout = pre_hp > 0 and target["hp"] <= 0

    target.setdefault("stats", _default_stats())
    target["stats"]["damage_taken"] = target["stats"].get("damage_taken", 0) + dmg
    taken_type_key = damage_taken_key(damage_type)
    target["stats"][taken_type_key] = target["stats"].get(taken_type_key, 0) + dmg
    if knockout:
        target["stats"]["times_downed"] = target["stats"].get("times_downed", 0) + 1

    if source is not None:
        source.setdefault("stats", _default_stats())
        source["stats"]["damage_dealt"] = source["stats"].get("damage_dealt", 0) + dmg
        type_key = damage_dealt_key(damage_type)
        source["stats"][type_key] = source["stats"].get(type_key, 0) + dmg
        if knockout:
            source["stats"]["knockouts"] = source["stats"].get("knockouts", 0) + 1

    return DamageTaken(
        dmg=dmg,
        hp_delta=target["hp"] - pre_hp,
        temp_delta=target["temp_hp"] - pre_temp,
        knockout=knockout,
    )


# ---- Dealing it, and what that sets off ----


@dataclass
class DamageDealt:
    """What deal_damage leaves the window to finish, in its order: the
    damage taken (after Resistance and Immunity), whether that's owed a
    Concentration save (DamageMixin._ask_concentration_save asks it), and
    what the hit triggers, fired after that (DamageOutcome, KnockoutOutcome,
    then bloodied_outcomes', judged once the save is settled)."""

    taken: int
    # Whether the target was Bloodied before the hit.
    was_bloodied: bool
    concentration_save: bool = False
    outcomes: list[Outcome] = field(default_factory=list)


def deal_damage(
    step: Step,
    target: dict,
    parts: list[tuple[int, str]],
    source: dict | None,
    check_resistance: bool,
    saved: bool,
    *,
    critical: bool,
    state_before: str,
    drops_to: int,
    ask_concentration: bool,
) -> DamageDealt:
    """One hit on target, of each (amount, damage type) in parts, and what
    the hit does to it: falling Unconscious, a Concentration save owed,
    failed Death Saving Throws if it was at 0 Hit Points already
    (`state_before`, its death state before the hit: two if the hit is
    `critical`, see take_damage_at_zero_hp). It drops to no fewer than
    `drops_to` Hit Points, what the window asked it drops to instead of 0
    (DamageMixin._drops_to_instead: Relentless Endurance); if that's above
    0, the hit leaves it there, and it isn't knocked out."""
    taken = 0
    knockout = False
    was_bloodied = "Bloodied" in target.get("conditions", [])
    for amount, damage_type in parts:
        dmg, downed = damage_target(
            step,
            target,
            amount,
            damage_type,
            source,
            check_resistance,
            saved,
            floor=drops_to,
        )
        taken += dmg
        knockout = knockout or downed
    if drops_to:
        points = "Hit Point" if drops_to == 1 else "Hit Points"
        step.log(
            f"{target['name']} drops to {target['hp']} {points} instead of 0",
            character=target["name"],
        )
    if taken > 0 and state_before in ("dying", "stabilized"):
        take_damage_at_zero_hp(step, target, taken, critical)
    note_health_change(step, target)
    if taken > 0:
        # Badges that end as their bearer takes damage (Sleep), is left
        # without Temporary Hit Points (Armor of Agathys) or deals damage
        # (Invisibility): plan step 9.6.
        end_when(step, target, EndEvent.TAKES_DAMAGE)
        if not target.get("temp_hp"):
            end_when(step, target, EndEvent.NO_TEMP_HP)
        if source is not None and source is not target:
            end_when(step, source, EndEvent.DEALS_DAMAGE)
    # A summon whose spec says so vanishes at 0 HP (a drake), once
    # what it was concentrating on has ended.
    vanishes = knockout and vanishes_at_zero_hp(target)

    # A creature that makes Death Saving Throws falls Unconscious at
    # 0 HP (which also ends its Concentration); any other one dies.
    if knockout and not vanishes and death_state(target) != "dead":
        add_condition(step, target, Condition.UNCONSCIOUS.value)

    dealt = DamageDealt(taken, was_bloodied)
    if "Concentrating" in target.get("conditions", []):
        if knockout:
            remove_condition(step, target, "Concentrating", source=target)
        elif taken > 0 and ask_concentration:
            # Only damage taken forces a save (damage soaked by
            # temporary HP still counts); 0 after immunity doesn't.
            dealt.concentration_save = True
    if vanishes:
        vanish_at_zero_hp(step, target)
    if source is not None and source is not target and taken > 0:
        # What the one damaged answers it with (Hellish Rebuke), asked
        # with the rest of the Apply's triggers.
        dealt.outcomes.append(DamageOutcome(source, target, taken))
    if source is not None and source is not target and knockout:
        # What the one that did it gets for it (Dark One's Blessing).
        dealt.outcomes.append(KnockoutOutcome(source, target))
    return dealt


def bloodied_outcomes(
    dealt: DamageDealt, target: dict, source: dict | None
) -> list[Outcome]:
    """What the one the hit left Bloodied does then (Harvest Undead). The
    window asks it after the hit's Concentration save, as that save, lost,
    can take a badge's Hit Point maximum off, and Bloodied with it."""
    if (
        not dealt.was_bloodied
        and target["hp"] > 0
        and "Bloodied" in target.get("conditions", [])
    ):
        return [BloodiedOutcome(target, source)]
    return []


def damage_target(
    step: Step,
    target: dict,
    amount: int,
    damage_type: str,
    source: dict | None,
    check_resistance: bool,
    saved: bool,
    floor: int = 0,
) -> tuple[int, bool]:
    """Deal one damage type to target, halved first if it saved, leaving
    it no fewer Hit Points than `floor` (what it drops to instead of 0:
    Relentless Endurance's 1, Relentless Rage's twice the Barbarian's
    level, even if that's more). Returns (the damage dealt, whether it
    took target to 0 HP)."""
    source_name = source["name"] if source is not None else None
    dmg = amount // 2 if saved else amount
    outcome = None
    if check_resistance:
        dmg, outcome = damage_type_modifier(target, dmg, damage_type)
    defense = outcome
    if saved:
        outcome = f"saved, {outcome}" if outcome else "saved"

    taken = take_damage(target, dmg, damage_type, source, floor)
    knockout = taken.knockout
    damage_value = {
        "hp_delta": taken.hp_delta,
        "temp_delta": taken.temp_delta,
        "dmg": dmg,
        "damage_type": damage_type,
        "source_name": source_name,
        "target_name": target["name"],
        "knockout": knockout,
        "outcome": outcome,
    }
    source_suffix = f" from {source_name}" if source_name else ""
    outcome_suffix = f" ({outcome})" if outcome else ""
    readable = step.log(
        f"{target['name']} takes {dmg} {damage_type} damage{source_suffix}{outcome_suffix}",
        character=target["name"],
        action=Action.DAMAGE,
        value=damage_value,
    )
    if readable:
        note_damage_defense(target, damage_type, defense)

    # Auto-apply bloodied condition, attributed to whoever dealt the damage
    apply_bloodied(step, target, source=source)

    step.result.change(target)
    return dmg, knockout


def take_damage_at_zero_hp(step: Step, char: dict, damage: int, critical: bool):
    """Char, dying or Stable at 0 Hit Points, took `damage` (2024 rules,
    Damage at 0 Hit Points): one failed Death Saving Throw, two from a
    Critical Hit, and death if it's at least char's Hit Point maximum.
    A Stable creature stops being Stable: its saves start over (they
    were reset as it became Stable) with these failures."""
    hit = damage_at_zero_hp(char, damage, critical)
    failures, massive = hit.failures, hit.massive
    ends_stable, newly_dead = hit.ends_stable, hit.newly_dead
    name = char["name"]
    if massive:
        text = (
            f"{name} dies: {damage} damage at 0 HP is at least their"
            " Hit Point maximum"
        )
    else:
        saves = "2 death saves" if failures == 2 else "a death save"
        crit = " (Critical Hit)" if critical else ""
        stable = ", no longer Stable" if ends_stable else ""
        text = (
            f"{name} fails {saves} from damage at 0 HP{crit}{stable}"
            f" ({char['death_saves_fail']}/3 fails)"
        )
        if newly_dead:
            text += " and dies"
    step.log(
        text,
        character=name,
        action=Action.DEATH_SAVE_FAIL,
        # A dict, unlike a rolled save's newly_dead, for the replay
        # (Combat/Fight/log.py's apply_replay_action) to do the same.
        value={
            "newly_dead": newly_dead,
            "failures": failures,
            "ends_stable": ends_stable,
            "massive": massive,
            "target_name": name,
        },
    )
    if newly_dead and "Concentrating" in char.get("conditions", []):
        remove_condition(step, char, "Concentrating", source=char)
    if newly_dead:
        summons_die_with(step, char)
