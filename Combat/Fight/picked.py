"""What the Use / Cast dialog applies for a picker row picked and nothing
edited, with no Qt: for a row a trigger fires (ConditionsMixin._apply_row,
from TurnPanelMixin._use_trigger) and a monster's action button. Moved out of
Combat/CombatUIQt/conditions_mixin.py (Notes/combat-effects-plan.md, step
9.1; the refactor plan's step 5.4 moves the apply path's pieces here).

A row that answers its owner's own hit (`answers`, the AttackOutcome a
trigger fired on, whose attacker is the owner) is used with what that hit
says (step 9.1): a Critical Hit rolls its damage
dice twice (Rules Glossary, Critical Hit: "roll the attack's damage dice
twice"; Sneak Attack, Divine Smite), and a damage type left to choose takes
the type of the weapon the hit was made with (Sneak Attack: "the damage is
the weapon's type"). A row answering a hit on its owner (Fire Shield's
flames, Hellish Rebuke) isn't: the attacker's Critical Hit doubles only the
attacker's own dice.
"""

from dataclasses import replace

from .saves import (
    ATTACK_ROLL,
    DAMAGE_AMOUNT,
    DEFAULT_SAVE_DC,
    HEALING,
    TEMP_HP,
    CustomEffect,
    EffectOption,
    read_damage,
    read_hit_points,
)


def option_duration(option: EffectOption) -> dict | None:
    """How long what a picked row gives lasts, as a CustomEffect says it."""
    if option.until is not None:
        return {"until": option.until[0], "of": option.until[1]}
    if option.duration_seconds:
        return {"seconds": option.duration_seconds}
    return None


def _hit_weapon_type(answers: object) -> str | None:
    """The damage type of the attacker's weapon the hit `answers` was made
    with (its row is the weapon's name), if it was one."""
    row = getattr(answers, "row", "")
    attacker = getattr(answers, "attacker", None)
    if not row or not isinstance(attacker, dict):
        return None
    for weapon in attacker.get("_weapons_objects") or ():
        if weapon.name == row:
            return weapon.damage_type.value
    return None


def _typed_like_the_hit(option: EffectOption, answers: object) -> EffectOption:
    """`option` with a damage type left to choose given the hit's weapon's."""
    if not any(roll.damage_type is None for roll in option.rolls):
        return option
    kind = _hit_weapon_type(answers)
    if kind is None:
        return option
    rolls = tuple(
        replace(roll, damage_type=kind) if roll.damage_type is None else roll
        for roll in option.rolls
    )
    return replace(option, rolls=rolls)


def picked_effect(
    option: EffectOption,
    last_save: dict,
    answers: object = None,
    owner: dict | None = None,
) -> CustomEffect | None:
    """What the Custom Effect dialog applies for `option` picked and nothing
    edited: its roll, damage rolled now (twice over for a Critical Hit),
    conditions, duration and costs. A DC or attack bonus it leaves unset is
    the dialog's last (`last_save`, ConditionsMixin._custom_save). `answers`:
    the hit a fired row of `owner`'s comes with, which counts only if owner
    made it (see the module docstring). None when its
    damage can't be applied as it is (a damage type to choose)."""
    if answers is None or getattr(answers, "attacker", None) is not owner:
        answers = None  # not owner's own hit: nothing of it counts here
    option = _typed_like_the_hit(option, answers) if answers is not None else option
    is_attack = option.roll == ATTACK_ROLL
    text = option.damage_at(option.slot_level)
    damage: list[tuple[int, str]] = []
    critical: list[tuple[int, str]] = []
    hit_points = 0
    if option.amount_kind == DAMAGE_AMOUNT:
        damage, problem = read_damage(text)
        if not problem:
            critical, problem = read_damage(text, critical=True)
    else:
        hit_points, problem = read_hit_points(text, option.amount_kind)
    if problem:
        return None
    if getattr(answers, "critical", False) and critical:
        damage = critical
    dc = option.dc if option.dc is not None else last_save.get("dc")
    bonus = option.bonus if option.bonus is not None else last_save.get("bonus")
    return CustomEffect(
        name=option.name,
        condition=option.condition,
        duration=option_duration(option),
        damage=damage,
        critical_damage=critical if is_attack else [],
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
