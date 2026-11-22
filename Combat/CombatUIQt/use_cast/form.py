"""What the Use / Cast dialog reads from its boxes, without Qt: the rolls
made at the table and typed in, and the copies of an effect its Times box
asks for (Notes/combat-ui-refactor-plan.md, step 3a).

Each reader takes the boxes' text and returns what it means, or raises
FormError with what to tell the GM; the dialog shows that under its form.

A box takes one roll for each of the Times ("17, 9, nat 20"), in order; a
short list rolls the rest, and a blank one is rolled (combat-effects plan
step 8.5)."""

import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import TypeVar

from ..amounts import parse_amount
from ..attack_rolls import AttackRoll, parse_attack_roll
from ..saves import (
    ATTACK_ROLL,
    CONDITION_JOINER,
    DAMAGE_AMOUNT,
    HEALING,
    TEMP_HP,
    CustomEffect,
    EffectOption,
    condition_names,
    read_damage,
    read_hit_points,
)

_NATURAL_ROLL = re.compile(r"nat(?:ural)?\s*\d+", re.IGNORECASE)
_WHOLE_NUMBER = re.compile(r"-?\d+")
# Dice, stood in for by a number when only the type in the text matters.
DICELESS = re.compile(r"\d+d\d+")


class FormError(ValueError):
    """What's wrong with something typed in the dialog, as the GM reads it."""


_T = TypeVar("_T")


def read_or_say(read: Callable[[], _T], say: Callable[[str], None]) -> _T | None:
    """What `read()` returns, or None having passed what's wrong to `say`."""
    try:
        return read()
    except FormError as error:
        say(str(error))
        return None


def rolls_in(text: str, times: int) -> list[str]:
    """The rolls typed in a box, one per time."""
    parts = [part.strip() for part in text.split(",")]
    if len(parts) > times:
        raise FormError(f"'{text}': {len(parts)} rolls for Times {times}.")
    return parts


def typed_totals(texts: dict[int, str], times: int) -> dict[int, list[int | None]]:
    """The saving throw totals typed, a list for each target (by key): a
    total ("14") or a sum ("9+5"), as an attack's. A total can be negative: a
    low roll with a negative save. A natural 20 or 1 is nothing special on a
    save, so it's the total that's wanted."""
    totals: dict[int, list[int | None]] = {}
    for key, raw in texts.items():
        text = raw.strip()
        if not text:
            continue
        for part in rolls_in(text, times):
            if not part:
                totals.setdefault(key, []).append(None)
                continue
            if _NATURAL_ROLL.fullmatch(part):
                raise FormError(
                    f"'{part}': a natural roll is nothing special on a"
                    " save. Type the total instead."
                )
            total = int(part) if _WHOLE_NUMBER.fullmatch(part) else None
            if total is None:
                total = parse_amount(part)
            if total is None:
                raise FormError(f"'{part}' isn't a saving throw total.")
            totals.setdefault(key, []).append(total)
    return totals


def typed_attacks(
    texts: dict[int, str], times: int
) -> dict[int, list[AttackRoll | None]]:
    """The attack rolls typed, a list for each target (by key)."""
    rolls: dict[int, list[AttackRoll | None]] = {}
    for key, raw in texts.items():
        text = raw.strip()
        if not text:
            continue
        for part in rolls_in(text, times):
            roll = parse_attack_roll(part) if part else None
            if part and roll is None:
                raise FormError(
                    f"'{part}' isn't an attack roll. Try 17, 12+5 or nat 20."
                )
            rolls.setdefault(key, []).append(roll)
    return rolls


def typed_extras(
    texts: dict[tuple[int, str], str], times: int
) -> dict[int, dict[str, list[int | None]]]:
    """The extra damage rolled at the table, by target key and what gives it
    (the label of its box), a list for each."""
    extras: dict[int, dict[str, list[int | None]]] = {}
    for (key, label), raw in texts.items():
        text = raw.strip()
        if not text:
            continue
        for part in rolls_in(text, times):
            total = None
            if part and _WHOLE_NUMBER.fullmatch(part):
                total = int(part)
            elif part:
                total = parse_amount(part)
            if part and (total is None or total < 0):
                raise FormError(f"'{part}' isn't an amount of damage for {label}.")
            extras.setdefault(key, {}).setdefault(label, []).append(total)
    return extras


def typed_maximum(text: str, target_keys: list[int]) -> dict[int, int]:
    """The Hit Point maximum typed, by target key: one total for all, or one
    per target. Blank: none typed."""
    text = text.strip()
    if not text:
        return {}
    parts = [part.strip() for part in text.split(",")]
    if len(parts) not in (1, len(target_keys)):
        raise FormError(
            f"'{text}': one Hit Point maximum for all, or one for each"
            f" of the {len(target_keys)} targets."
        )
    if not all(_WHOLE_NUMBER.fullmatch(part) for part in parts):
        raise FormError(f"'{text}' isn't a Hit Point maximum.")
    values = [int(part) for part in parts] * (
        len(target_keys) if len(parts) == 1 else 1
    )
    return dict(zip(target_keys, values))


def nth(lists: dict, index: int) -> dict:
    """What was typed for time `index` (from 0), by key; a nested dict (the
    extras) by its keys too. A blank or missing one is left out, so it's
    rolled."""
    picked = {}
    for key, value in lists.items():
        if isinstance(value, dict):
            inner = nth(value, index)
            if inner:
                picked[key] = inner
        elif index < len(value) and value[index] is not None:
            picked[key] = value[index]
    return picked


def repeated(
    effect: CustomEffect,
    times: int,
    *,
    amount_text: str,
    damage_type: str | None,
    kind: str,
    typed_rolls: dict[str, dict],
) -> list[CustomEffect]:
    """`effect` `times` over: each with its own damage roll (from
    `amount_text`, the Damage box), named "Scorching Ray (2 of 3)" in the
    log, only the first costing the source anything, and each with its own
    of the rolls typed in ("17, 9": the first time's 17, the second's 9).
    `typed_rolls` holds the "totals", "attacks" and "extras" read for all
    the times."""
    effects = []
    for index in range(times):
        each = replace(effect, name=f"{effect.name} ({index + 1} of {times})")
        if index:
            damage: list[tuple[int, str]] = []
            critical: list[tuple[int, str]] = []
            hit_points = 0
            if kind == DAMAGE_AMOUNT:
                damage, _ = read_damage(amount_text, damage_type)
                if effect.attack_bonus is not None:
                    critical, _ = read_damage(amount_text, damage_type, critical=True)
            else:
                hit_points, _ = read_hit_points(amount_text, kind)
            each = replace(
                each,
                damage=damage,
                critical_damage=critical,
                healing=hit_points if kind == HEALING else 0,
                temp_hp=hit_points if kind == TEMP_HP else 0,
                slot_level=None,
                action_cost=None,
                concentration=False,
                area=None,
                typed_attacks=nth(typed_rolls["attacks"], index),
                typed_totals=nth(typed_rolls["totals"], index),
                typed_extras=nth(typed_rolls["extras"], index),
                pick=None,
                row=effect.pick.name if effect.pick is not None else "",
            )
        effects.append(each)
    return effects


@dataclass(frozen=True)
class FormValues:
    """What the dialog's boxes hold as Apply is pressed, as plain values
    (UseCastDialog._read_form reads them). Everything building the effect
    needs is here, so it's built and checked without Qt."""

    # The roll: ATTACK_ROLL, or a saving throw (and its ability, None for no
    # roll at all).
    roll: str
    ability: str | None
    # The Condition box as typed, and the condition names it may match.
    condition_text: str
    suggestions: list[str]
    # The Damage box, what it holds (DAMAGE_AMOUNT, HEALING, TEMP_HP) and the
    # damage type picked for damage with none typed.
    amount_kind: str
    amount_text: str
    damage_type: str | None
    # What was picked, the damage text it filled in, and whether the source
    # can spend it (a caster is picked).
    pick: EffectOption | None
    pick_damage: str
    has_caster: bool
    # Who it's used on: targets picked, or the pick goes on its user, or an
    # area aimed on the map is kept there.
    has_targets: bool
    on_itself: bool
    keeps_area: bool
    name: str = ""
    notes: str = ""
    duration: dict | None = None
    count_resistances: bool = True
    slot_level: int | None = None
    action_cost: str | None = None
    concentration: bool = False
    # The kept area acting again (its key), and the area aimed to keep.
    from_area: str = ""
    area: dict | None = None
    cover_origin: list | None = None
    attack_bonus: int = 0
    dc: int = 0
    mode: str = "Neutral"
    half_on_save: bool = True
    use_legendary_resistance: bool = False
    repeat_save: bool = False
    # Each attack target's Shield box, by target key.
    shields: dict[int, bool] = field(default_factory=dict)
    # The push box is shown and ticked.
    pushes: bool = False

    @property
    def is_attack(self) -> bool:
        return self.roll == ATTACK_ROLL

    @property
    def save_ability(self) -> str | None:
        """The saving throw's ability; None for an attack or no roll."""
        return None if self.is_attack else self.ability


@dataclass(frozen=True)
class Amount:
    """The Damage box read once: damage by type, or Hit Points. Reading it
    rolls its dice, so it's read once and passed on."""

    damage: list[tuple[int, str]]
    hit_points: int


@dataclass(frozen=True)
class TypedRolls:
    """The rolls made at the table, read for all the Times (typed_totals,
    typed_attacks, typed_extras, typed_maximum)."""

    totals: dict = field(default_factory=dict)
    attacks: dict = field(default_factory=dict)
    extras: dict = field(default_factory=dict)
    maximum: dict = field(default_factory=dict)


def read_amount(values: FormValues) -> Amount:
    """The Damage box's damage or Hit Points."""
    if values.amount_kind == DAMAGE_AMOUNT:
        damage, problem = read_damage(values.amount_text, values.damage_type)
        hit_points = 0
    else:
        hit_points, problem = read_hit_points(values.amount_text, values.amount_kind)
        damage = []
    if problem:
        raise FormError(problem)
    return Amount(damage, hit_points)


def condition_of(values: FormValues) -> str:
    """The Condition box's conditions, each as the rules name it ("stunned"
    is Stunned) and joined ("Frightened + Incapacitated" is both)."""
    return CONDITION_JOINER.join(
        next((s for s in values.suggestions if s.lower() == typed.lower()), typed)
        for typed in condition_names(values.condition_text)
    )


def check_applicable(values: FormValues, amount: Amount) -> bool:
    """True when Apply has someone to use it on and something to do."""
    pick = values.pick
    keeps_area = values.keeps_area
    if not values.has_targets and not keeps_area and not values.on_itself:
        raise FormError(
            "Target missing: pick one at the top, or keep the area on the map."
        )
    # A pick the source spends (a feature with no numbers) is enough, and so
    # is one that ends conditions or only moves its target (Push).
    spends = pick is not None and pick.is_tracked and values.has_caster
    ends = pick is not None and (bool(pick.ends_conditions) or pick.push is not None)
    if (
        not keeps_area
        and not values.is_attack
        and values.save_ability is None
        and not amount.damage
        and not amount.hit_points
        and not condition_of(values)
        and not spends
        and not ends
    ):
        raise FormError("Add a saving throw, damage, healing or a condition.")
    return True


def build_effect(values: FormValues, amount: Amount, rolls: TypedRolls) -> CustomEffect:
    """The effect Apply uses on every target (the first of the Times; see
    repeated for the rest). A critical hit's damage is rolled here, after
    the hit's own, as the dialog always rolled them."""
    pick = values.pick
    kind = values.amount_kind
    critical_damage = []
    if values.is_attack and kind == DAMAGE_AMOUNT:
        critical_damage, _ = read_damage(
            values.amount_text, values.damage_type, critical=True
        )
    return CustomEffect(
        name=values.name.strip(),
        condition=condition_of(values),
        duration=values.duration,
        notes=values.notes,
        damage=amount.damage,
        critical_damage=critical_damage,
        count_resistances=values.count_resistances,
        healing=amount.hit_points if kind == HEALING else 0,
        temp_hp=amount.hit_points if kind == TEMP_HP else 0,
        slot_level=values.slot_level,
        action_cost=values.action_cost,
        concentration=values.concentration,
        from_area=values.from_area,
        attack_bonus=values.attack_bonus if values.is_attack else None,
        typed_attacks=nth(rolls.attacks, 0),
        typed_extras=nth(rolls.extras, 0),
        ability=values.save_ability,
        dc=values.dc,
        mode=values.mode,
        half_on_save=values.half_on_save,
        use_legendary_resistance=values.use_legendary_resistance,
        repeat_save=values.repeat_save,
        typed_totals=nth(rolls.totals, 0),
        typed_hit_point_maximum=rolls.maximum,
        shields=values.shields if values.is_attack else {},
        pick=pick,
        weapon_attack=pick.weapon_attack if pick is not None else None,
        # A total with no dice, not the pick's own damage, was rolled at the
        # table: a hit's extra damage isn't added to it.
        typed_damage=bool(amount.damage)
        and not DICELESS.search(values.amount_text)
        and values.amount_text != values.pick_damage,
        area=values.area,
        cover_origin=values.cover_origin,
        push=pick.push if pick is not None and values.pushes else None,
    )
