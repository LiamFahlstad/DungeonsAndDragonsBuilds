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
from dataclasses import replace
from typing import TypeVar

from ..amounts import parse_amount
from ..attack_rolls import AttackRoll, parse_attack_roll
from ..saves import (
    DAMAGE_AMOUNT,
    HEALING,
    TEMP_HP,
    CustomEffect,
    read_damage,
    read_hit_points,
)

_NATURAL_ROLL = re.compile(r"nat(?:ural)?\s*\d+", re.IGNORECASE)
_WHOLE_NUMBER = re.compile(r"-?\d+")


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
