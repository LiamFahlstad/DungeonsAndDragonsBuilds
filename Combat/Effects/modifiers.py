"""The modifiers on a combatant, and what they make of a roll against it or by
it. A combatant is the combat UI's dict; its "conditions" are names, each a
rules condition ("Restrained"), the same under a longer custom name
("Restrained by vines"), or a badge, which has no rules.

What a modifier says counts in a roll the simulator makes. One with a `when`
(where the attacker is, what it can see) is never counted, only noted, since
the simulator doesn't know positions (plan principle 8). A total rolled at the
table counts as it is, so only the notes it can't have known about come with
it. The roll modes are the UI's text: "Neutral", "Advantage", "Disadvantage".
"""

from collections.abc import Iterable
from dataclasses import dataclass

from Core.Definitions import Condition
from Model.Content.CombatModifiers import (
    ArmorClass,
    AttacksAgainst,
    AutoFail,
    ConditionImmunity,
    CriticalHitsAgainst,
    D20Bonus,
    D20Mode,
    D20Test,
    Modifier,
    Resistance,
    RollMode,
)
from Model.Content.RulesConditions import CONDITION_RULES, conditions_given_by

NEUTRAL = "Neutral"


def rules_condition(name: str) -> Condition | None:
    """The rules condition a condition's name is: its own name, or one that
    starts with it and a space ("Restrained by vines"). None for a badge."""
    for condition in Condition:
        if name == condition.value or name.startswith(f"{condition.value} "):
            return condition
    return None


def held_conditions(char: dict) -> list[Condition]:
    """The rules conditions char has, with those they give (Unconscious gives
    Incapacitated and Prone), each once. One that another makes it immune to
    "doesn't affect you in any way" (Petrified's Poisoned), so it's left out."""
    held: list[Condition] = []
    for name in char.get("conditions", []):
        condition = rules_condition(name)
        if condition is not None:
            held += [c for c in conditions_given_by(condition) if c not in held]
    immune = {
        c
        for held_condition in held
        for m in CONDITION_RULES[held_condition]
        if isinstance(m, ConditionImmunity)
        for c in m.conditions
    }
    return [c for c in held if c not in immune]


def has_condition(char: dict, condition: Condition) -> bool:
    """Whether char has `condition`, given by another or under a longer name."""
    return condition in held_conditions(char)


def modifiers_on(char: dict) -> list[tuple[Condition, Modifier]]:
    """Each modifier on char, with the condition it comes from."""
    return [
        (condition, modifier)
        for condition in held_conditions(char)
        for modifier in CONDITION_RULES[condition]
    ]


@dataclass(frozen=True)
class RollPlan:
    """How a d20 roll is made once the modifiers count: its mode, why it
    fails without a roll (if it does), and what the GM should know."""

    mode: str
    auto_fail: str = ""
    notes: tuple[str, ...] = ()


def _applies(modifier, test: D20Test, ability: str | None) -> bool:
    if test not in modifier.tests:
        return False
    return not modifier.abilities or any(
        a.short_name == ability for a in modifier.abilities
    )


def _and(labels: list[str]) -> str:
    if len(labels) == 1:
        return labels[0]
    return f"{', '.join(labels[:-1])} and {labels[-1]}"


def combine_modes(
    mode: str, given: list[tuple[str, RollMode]]
) -> tuple[str, list[str]]:
    """`mode` (the one asked for) with the modes `given`, by what gives each:
    Advantage and Disadvantage cancel out however many of each there are.
    Returns the mode and the notes saying why it changed."""
    if not given:
        return mode, []
    modes = {str(m) for _, m in given} | ({mode} - {NEUTRAL})
    notes = [f"{label}: {m}" for label, m in given]
    if len(modes) == 1:
        return modes.pop(), notes
    if mode != NEUTRAL and all(m != mode for _, m in given):
        # Only the asked-for mode is gone: "Restrained: Disadvantage,
        # cancelling Advantage".
        theirs = given[0][1]
        return NEUTRAL, [
            f"{_and([label for label, _ in given])}: {theirs}," f" cancelling {mode}"
        ]
    return NEUTRAL, [*notes, "Advantage and Disadvantage cancel out"]


def _uncounted(modifier) -> str:
    """What a modifier with a `when`, or one not counted yet, says, for a
    note: "-2 a level", "Advantage if the attacker is within 5 feet of it"."""
    when = f" if {modifier.when}" if modifier.when else ""
    if isinstance(modifier, D20Bonus):
        each = " a level" if modifier.per_level else ""
        return f"{modifier.amount}{each}{when}"
    if isinstance(modifier, AutoFail):
        return f"automatic failure{when}"
    return f"{modifier.mode}{when}"


def _plan(
    mode: str,
    sources: Iterable[tuple[str, Modifier]],
    test: D20Test,
    ability: str | None,
    typed: bool,
) -> RollPlan:
    """The roll of `test` once `sources` count: (label, modifier) pairs, each
    a modifier on the roller (or, for AttacksAgainst, on its target)."""
    given: list[tuple[str, RollMode]] = []
    # What isn't counted, by what gives it: "Exhaustion (not counted): -2 a
    # level", "Tiger is Prone (not counted): Advantage if ..., Disadvantage
    # if ...".
    uncounted: dict[str, list[tuple[str, RollMode | None]]] = {}
    for label, modifier in sources:
        if isinstance(modifier, AttacksAgainst):
            if test != D20Test.ATTACK_ROLL:
                continue
        elif isinstance(modifier, (D20Mode, AutoFail, D20Bonus)):
            if not _applies(modifier, test, ability):
                continue
        else:
            continue
        if isinstance(modifier, AutoFail) and not modifier.when:
            return RollPlan(mode, f"{label}: automatic failure")
        if typed:
            continue  # rolled at the table, the way the GM saw fit
        if isinstance(modifier, (D20Mode, AttacksAgainst)) and not modifier.when:
            given.append((label, modifier.mode))
        else:
            # A `when` the GM judges; a D20Bonus isn't counted yet (step 3.3).
            judged = getattr(modifier, "mode", None)
            uncounted.setdefault(label, []).append((_uncounted(modifier), judged))
    mode, notes = combine_modes(mode, given)
    for label, what in uncounted.items():
        # One that would cancel the mode counted says so: an Unconscious
        # target's Advantage, from farther than 5 feet, is a straight roll.
        texts = [
            (
                f"{text}, a straight roll then"
                if judged is not None and mode != NEUTRAL and judged != mode
                else text
            )
            for text, judged in what
        ]
        notes.append(f"{label} (not counted): {'; '.join(texts)}")
    return RollPlan(mode, "", tuple(notes))


def save_plan(char: dict, ability: str, mode: str, typed: bool = False) -> RollPlan:
    """Char's saving throw of `ability` ("DEX"), asked for with `mode`.
    `typed`: a total rolled at the table, which only an automatic failure
    changes; its mode and bonuses are the GM's."""
    sources = ((c.value, m) for c, m in modifiers_on(char))
    return _plan(mode, sources, D20Test.SAVING_THROW, ability, typed)


def _whose(char: dict | None, condition: Condition) -> str:
    """A condition in a note about an attack, which has two sides: "Tiger is
    Restrained", "Pirate's Exhaustion"."""
    name = char["name"] if char is not None else "The attacker"
    if condition == Condition.EXHAUSTION:
        return f"{name}'s {condition.value}"
    return f"{name} is {condition.value}"


def attack_plan(
    attacker: dict | None, target: dict | None, mode: str, typed: bool = False
) -> RollPlan:
    """An attack roll by attacker against target (either None: unknown, or
    several), asked for with `mode`: the attacker's own modifiers, then the
    target's AttacksAgainst. `typed`: rolled at the table, as save_plan."""
    sources: list[tuple[str, Modifier]] = []
    if attacker is not None:
        sources += [
            (_whose(attacker, c), m)
            for c, m in modifiers_on(attacker)
            if not isinstance(m, AttacksAgainst)
        ]
    if target is not None:
        sources += [
            (_whose(target, c), m)
            for c, m in modifiers_on(target)
            if isinstance(m, AttacksAgainst)
        ]
    return _plan(mode, sources, D20Test.ATTACK_ROLL, None, typed)


def hit_notes(target: dict) -> list[str]:
    """What the GM should check about a hit on target: a Critical Hit the
    simulator can't tell (Paralyzed: "if the attacker is within 5 feet")."""
    notes = []
    for condition, modifier in modifiers_on(target):
        if isinstance(modifier, CriticalHitsAgainst):
            label = _whose(target, condition)
            if modifier.when:
                notes.append(
                    f"{label}: a Critical Hit if {modifier.when} (not counted)"
                )
            else:
                notes.append(f"{label}: a Critical Hit")
    return notes


def armor_class_bonus(char: dict) -> int:
    """What char's modifiers add to its AC."""
    return sum(m.bonus for _, m in modifiers_on(char) if isinstance(m, ArmorClass))


def resists(char: dict, damage_type: str) -> bool:
    """Whether char's modifiers give it Resistance to `damage_type`."""
    return any(
        isinstance(m, Resistance)
        and (not m.damage_types or any(t.value == damage_type for t in m.damage_types))
        for _, m in modifiers_on(char)
    )


def resists_all_damage(char: dict) -> bool:
    """Whether char's modifiers give it Resistance to all damage (Petrified):
    then a resisted hit says nothing about its own defenses."""
    return any(
        isinstance(m, Resistance) and not m.damage_types for _, m in modifiers_on(char)
    )


def immune_to_condition(char: dict, condition: str) -> bool:
    """Whether char's modifiers make it immune to `condition` (Petrified's
    Poisoned): then that says nothing about its own immunities."""
    return any(
        isinstance(m, ConditionImmunity)
        and any(c.value == condition for c in m.conditions)
        for _, m in modifiers_on(char)
    )
