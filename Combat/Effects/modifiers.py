"""The modifiers on a combatant, and what they make of a roll against it or by
it. A combatant is the combat UI's dict. Its modifiers come from three places:

- its "conditions", names, each a rules condition ("Restrained"), the same
  under a longer custom name ("Restrained by vines"), or a badge, which has no
  rules of its own (Model/Content/RulesConditions.py);
- its cover (its "visibility_states"), the most protective one;
- its lasting effects (active_effects.py): what a badge it has says it gives
  (Bless's 1d4, Shield of Faith's +2 AC), while it has the badge.

What a modifier says counts in a roll the simulator makes, a D20Bonus's dice
rolled and added, and a hit's extra damage (hit_plan) rolled with its damage:
the attacker's ExtraDamageOnHit, and the target's ExtraDamageFrom when the
attacker is the caster of the effect it's on; an AttacksAgainst `by_caster`
(Vex) counts only for that caster too. A `once` one counts for one attack
roll, which uses its badge up (used_up_by_attack). One with a `when` (where the attacker is, what it can see)
is never counted, only noted, since the simulator doesn't know positions
(plan principle 8). A total rolled at the table counts as it is, so only the
notes it can't have known about come with it. The roll modes are the UI's
text: "Neutral", "Advantage", "Disadvantage".
"""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from typing import TypeVar

from Core.Definitions import Ability, Condition, CreatureSize
from Core.Rules import ability_modifier
from Model.Content.CombatModifiers import (
    ArmorClass,
    ArmorClassBase,
    ArmorClassMinimum,
    AttackKind,
    AttacksAgainst,
    AutoFail,
    ConditionImmunity,
    CriticalHitsAgainst,
    D20Bonus,
    DamageImmunity,
    D20Mode,
    D20Test,
    ExtraDamageFrom,
    ExtraDamageOnHit,
    HitPointMaximum,
    Modifier,
    Resistance,
    RollMode,
    Size,
    Speed,
    Vulnerability,
    WhenHit,
    modifier_from_dict,
)
from Model.Content.RulesConditions import CONDITION_RULES, conditions_given_by
from Model.Creatures.Combatants import Visibility

from .active_effects import ActiveEffect, active_effects

NEUTRAL = "Neutral"

# What a modifier comes from: a rules condition, or the name of a cover or of
# a lasting effect's badge ("Half Cover", "Bless").
Source = Condition | str

# Cover (Rules Glossary): "Half Cover (+2 bonus to AC and Dexterity saving
# throws), Three-Quarters Cover (+5 bonus to AC and Dexterity saving
# throws)". Total Cover can't be targeted, which is the GM's to say.
COVER_RULES: dict[str, tuple[Modifier, ...]] = {
    Visibility.HALF_COVER.value: (
        ArmorClass(2),
        D20Bonus((D20Test.SAVING_THROW,), "2", (Ability.DEXTERITY,)),
    ),
    Visibility.THREE_QUARTERS_COVER.value: (
        ArmorClass(5),
        D20Bonus((D20Test.SAVING_THROW,), "5", (Ability.DEXTERITY,)),
    ),
}


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


def cover(char: dict) -> str | None:
    """Char's most protective cover ("Half Cover"), if it has any. COVER_RULES
    lists them from the least protective."""
    states = [s for s in char.get("visibility_states", []) if s in COVER_RULES]
    return max(states, key=list(COVER_RULES).index, default=None)


def _effects_with_modifiers(char: dict) -> list[tuple[ActiveEffect, Modifier]]:
    """Each modifier char's lasting effects give, with the effect: an
    effect's count while char has its badge."""
    badges = set(char.get("conditions", []))
    return [
        (
            effect,
            modifier_from_dict(data, f"{effect['name']} on {char.get('name')}"),
        )
        for effect in active_effects(char)
        if effect["name"] in badges
        for data in effect.get("modifiers") or ()
    ]


def effect_modifiers(char: dict) -> list[tuple[str, Modifier]]:
    """Each modifier char's lasting effects give, with the effect's name: an
    effect's count while char has its badge."""
    return [(effect["name"], m) for effect, m in _effects_with_modifiers(char)]


def modifiers_on(char: dict) -> list[tuple[Source, Modifier]]:
    """Each modifier on char, with what it comes from: its rules conditions'
    (the Condition), its cover's and its lasting effects' (their names)."""
    pairs: list[tuple[Source, Modifier]] = [
        (condition, modifier)
        for condition in held_conditions(char)
        for modifier in CONDITION_RULES[condition]
    ]
    where = cover(char)
    if where is not None:
        pairs += [(where, modifier) for modifier in COVER_RULES[where]]
    return pairs + effect_modifiers(char)


def _label(source: Source) -> str:
    return source.value if isinstance(source, Condition) else source


@dataclass(frozen=True)
class RollPlan:
    """How a d20 roll is made once the modifiers count: its mode, why it
    fails without a roll (if it does), what the GM should know, and what is
    added to it, by what gives it: (label, amount), ("Bless", "1d4"),
    ("Half Cover", "2"), rolled where the roll is made."""

    mode: str
    auto_fail: str = ""
    notes: tuple[str, ...] = ()
    bonuses: tuple[tuple[str, str], ...] = ()


def signed(amount: str) -> str:
    """A D20Bonus's amount with its sign: "+1d4", "-1d4", "+2"."""
    return amount if amount[:1] in ("+", "-") else f"+{amount}"


def bonus_reminder(plan: RollPlan) -> tuple[int, str]:
    """What a roll made at the table adds for `plan`'s bonuses, to show
    before it: the numbers' total and the dice, (2, "+1d4 -1d4")."""
    flat = sum(int(amount) for _, amount in plan.bonuses if "d" not in amount)
    dice = " ".join(signed(a) for _, a in plan.bonuses if "d" in a)
    return flat, dice


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
    bonuses: list[tuple[str, str]] = []
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
        elif (
            isinstance(modifier, D20Bonus)
            and not modifier.when
            and not modifier.per_level
        ):
            bonuses.append((label, modifier.amount))
        else:
            # A `when` the GM judges; Exhaustion's bonus a level, which
            # isn't tracked.
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
    return RollPlan(mode, "", tuple(notes), tuple(bonuses))


def save_plan(char: dict, ability: str, mode: str, typed: bool = False) -> RollPlan:
    """Char's saving throw of `ability` ("DEX"), asked for with `mode`.
    `typed`: a total rolled at the table, which only an automatic failure
    changes; its mode and bonuses are the GM's."""
    sources = ((_label(c), m) for c, m in modifiers_on(char))
    return _plan(mode, sources, D20Test.SAVING_THROW, ability, typed)


def _whose(char: dict | None, source: Source) -> str:
    """What a modifier comes from, in a note about an attack, which has two
    sides: "Tiger is Restrained", "Pirate's Exhaustion", "Pirate's Bless"."""
    name = char["name"] if char is not None else "The attacker"
    if isinstance(source, Condition) and source != Condition.EXHAUSTION:
        return f"{name} is {source.value}"
    return f"{name}'s {_label(source)}"


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
            if isinstance(m, AttacksAgainst) and not m.by_caster
        ]
        sources += [
            (_whose(target, effect["name"]), m)
            for effect, m in _by_caster_against(target, attacker)
        ]
    return _plan(mode, sources, D20Test.ATTACK_ROLL, None, typed)


def _by_caster_against(
    target: dict, attacker: dict | None
) -> list[tuple[ActiveEffect, AttacksAgainst]]:
    """The target's AttacksAgainst that count only for the creature that
    gave them (Vex), with their effect: those attacker gave it, or, with no
    attacker known, each as a `when` the GM judges ("the attacker is
    Edmund")."""
    found = []
    for effect, m in _effects_with_modifiers(target):
        if not isinstance(m, AttacksAgainst) or not m.by_caster:
            continue
        caster = effect.get("caster")
        if attacker is None:
            who = caster or "the creature that gave it"
            found.append((effect, replace(m, when=m.when or f"the attacker is {who}")))
        elif caster == attacker.get("name"):
            found.append((effect, m))
    return found


def used_up_by_attack(
    attacker: dict | None, target: dict | None
) -> list[tuple[dict, str]]:
    """The badges an attack roll by attacker against target uses up, as
    (who has it, its name): the attacker's own `once` D20Mode on attack
    rolls (Sap: "its next attack roll", whoever it's against), and the
    target's `once` AttacksAgainst that counted for it (Guiding Bolt; Vex,
    only for the attacker that gave it). Rolled here or at the table, the
    roll was made. One with a `when` is the GM's to take off, as it may not
    have counted."""
    used: list[tuple[dict, str]] = []
    if attacker is not None:
        used += [
            (attacker, effect["name"])
            for effect, m in _effects_with_modifiers(attacker)
            if isinstance(m, D20Mode) and m.once and not m.when
        ]
    if target is not None:
        used += [
            (target, effect["name"])
            for effect, m in _effects_with_modifiers(target)
            if isinstance(m, AttacksAgainst)
            and m.once
            and not m.when
            and not m.by_caster
        ]
        if attacker is not None:
            used += [
                (target, effect["name"])
                for effect, m in _by_caster_against(target, attacker)
                if m.once and not m.when
            ]
    unique: list[tuple[dict, str]] = []
    for char, name in used:
        if not any(char is c and name == n for c, n in unique):
            unique.append((char, name))
    return unique


def hit_notes(target: dict) -> list[str]:
    """What the GM should check about a hit on target: a Critical Hit the
    simulator can't tell (Paralyzed: "if the attacker is within 5 feet")."""
    notes = []
    for source, modifier in modifiers_on(target):
        if isinstance(modifier, CriticalHitsAgainst):
            label = _whose(target, source)
            if modifier.when:
                notes.append(
                    f"{label}: a Critical Hit if {modifier.when} (not counted)"
                )
            else:
                notes.append(f"{label}: a Critical Hit")
    return notes


HitExtra = ExtraDamageFrom | ExtraDamageOnHit


def hit_extras(
    attacker: dict | None, target: dict | None
) -> list[tuple[str, HitExtra]]:
    """The extra damage that can come with a hit by attacker on target, by
    what gives it ("Gabriel's Hunter's Mark"): the attacker's own
    ExtraDamageOnHit, and the target's ExtraDamageFrom of an effect the
    attacker gave it (the record's `caster`, a combatant's name, as every
    path that gives a badge fills it in). None without an attacker; only
    the attacker's own without a target (unknown, or several)."""
    if attacker is None:
        return []
    name = attacker["name"]
    pairs: list[tuple[str, HitExtra]] = [
        (f"{name}'s {effect['name']}", m)
        for effect, m in _effects_with_modifiers(attacker)
        if isinstance(m, ExtraDamageOnHit)
    ]
    if target is not None:
        pairs += [
            (f"{name}'s {effect['name']}", m)
            for effect, m in _effects_with_modifiers(target)
            if isinstance(m, ExtraDamageFrom) and effect.get("caster") == name
        ]
    return pairs


def extra_text(modifier: HitExtra) -> str:
    """What a hit's extra damage is, to show: "+1d6 Force on a hit",
    "+1d4 Radiant on a weapon hit"."""
    hit = "a weapon hit" if modifier.attacks == AttackKind.WEAPON else "a hit"
    when = f" if {modifier.when}" if modifier.when else ""
    return f"+{modifier.amount} {modifier.damage_type.value} on {hit}{when}"


@dataclass(frozen=True)
class HitPlan:
    """What a hit deals on top of its own damage: `extras`, (label, amount,
    damage type) each, ("Gabriel's Hunter's Mark", "1d6", "Force"), rolled
    where the damage is, and doubled on a Critical Hit; and what could come
    with it but isn't counted, for the GM. `at_table`: the labels whose
    amount is a total rolled at the table ("4"), to add as it is."""

    extras: tuple[tuple[str, str, str], ...] = ()
    notes: tuple[str, ...] = ()
    at_table: tuple[str, ...] = ()


def hit_plan(
    attacker: dict | None,
    target: dict | None,
    weapon_attack: bool | None,
    rolled: Mapping[str, int] | None = None,
) -> HitPlan:
    """The extra damage a hit by attacker on target deals (hit_extras).
    `weapon_attack`: whether the attack was made with a weapon, None when
    that isn't known (a monster's attack, a spell, an effect typed in).
    What only comes with a weapon attack adds nothing to one that isn't,
    and is noted, not counted, when that isn't known; one with a `when` is
    noted too (plan principle 8). `rolled`: totals rolled at the table, by
    label (principle 13); one counts whatever the rest would decide, as
    the GM typing it is the GM deciding it applies."""
    rolled = rolled or {}
    extras: list[tuple[str, str, str]] = []
    notes: list[str] = []
    at_table: list[str] = []
    for label, modifier in hit_extras(attacker, target):
        if label in rolled:
            extras.append((label, str(rolled[label]), modifier.damage_type.value))
            at_table.append(label)
            continue
        weapons_only = modifier.attacks == AttackKind.WEAPON
        if weapons_only and weapon_attack is False:
            continue
        if modifier.when or (weapons_only and weapon_attack is None):
            notes.append(f"{label} (not counted): {extra_text(modifier)}")
        else:
            extras.append((label, modifier.amount, modifier.damage_type.value))
    return HitPlan(tuple(extras), tuple(notes), tuple(at_table))


def _ability_bonus(char: dict, ability: Ability) -> int:
    scores = char.get("Ability Scores") or {}
    score = scores.get(ability.short_name)
    return ability_modifier(score) if isinstance(score, int) else 0


def _own_armor_modifiers(char: dict) -> list[tuple[str, Modifier]]:
    """The AC modifiers on char but its cover's, each once: two of the same
    effect don't add up (Rules Glossary, Combining Game Effects)."""
    where = cover(char)
    seen: list[tuple[str, Modifier]] = []
    for source, modifier in modifiers_on(char):
        pair = (_label(source), modifier)
        if (
            source != where
            and pair not in seen
            and isinstance(modifier, (ArmorClass, ArmorClassBase, ArmorClassMinimum))
        ):
            seen.append(pair)
    return seen


def _armor_class_steps(char: dict, stored: int) -> tuple[int, list[str]]:
    """Char's AC from `stored` (armor_class), and what made it that, in the
    order it counts: a base only when it beats `stored`, a floor only when
    it lifts the AC, every bonus and the cover ("Mage Armor 13 + DEX",
    "Shield of Faith +2", "Barkskin at least 17", "Half Cover +2")."""
    pairs = _own_armor_modifiers(char)
    armor, changes = stored, []
    best = None
    for label, m in pairs:
        if isinstance(m, ArmorClassBase):
            value = m.base + sum(_ability_bonus(char, a) for a in m.abilities)
            if value > armor:
                armor = value
                added = "".join(f" + {a.short_name}" for a in m.abilities)
                best = f"{label} {m.base}{added}"
    changes += [best] if best else []
    for label, m in pairs:
        if isinstance(m, ArmorClass):
            armor += m.bonus
            changes.append(f"{label} {m.bonus:+d}")
    floors = [
        (m.value, label) for label, m in pairs if isinstance(m, ArmorClassMinimum)
    ]
    if floors and max(floors)[0] > armor:
        armor, label = max(floors)
        changes.append(f"{label} at least {armor}")
    where = cover(char)
    if where is not None and cover_armor_bonus(char):
        armor += cover_armor_bonus(char)
        changes.append(f"{where} +{cover_armor_bonus(char)}")
    return armor, changes


def armor_class(char: dict, stored: int) -> int:
    """Char's AC with its modifiers in it, from the AC it has (`stored`: its
    stat block's or sheet's). The best of that and each ArmorClassBase, then
    what adds to it (ArmorClass), then at least each ArmorClassMinimum, and
    then its cover, which adds to whatever its AC is."""
    return _armor_class_steps(char, stored)[0]


def armor_class_text(char: dict, stored: int) -> str:
    """Char's AC as a card shows it: "15", or with what changes it, "17 (15;
    Shield of Faith +2)", "19 (13; Barkskin at least 17, Half Cover +2)"."""
    armor, changes = _armor_class_steps(char, stored)
    return f"{armor} ({stored}; {', '.join(changes)})" if changes else str(stored)


def armor_class_bonus(char: dict, stored: int | None = None) -> int:
    """What char's modifiers do to its AC, as a number added to `stored`
    (the AC it has; armor_class). With no AC to start from, only what adds
    to one counts: its cover's and its effects' ArmorClass."""
    if stored is None:
        return cover_armor_bonus(char) + sum(
            m.bonus for _, m in _own_armor_modifiers(char) if isinstance(m, ArmorClass)
        )
    return armor_class(char, stored) - stored


def cover_armor_bonus(char: dict) -> int:
    """What char's cover alone adds to its AC."""
    where = cover(char)
    if where is None:
        return 0
    return sum(m.bonus for m in COVER_RULES[where] if isinstance(m, ArmorClass))


def armor_class_notes(char: dict) -> list[str]:
    """What changes char's AC, but cover: "Shield of Faith: +2 AC", "Mage
    Armor: base AC 13 + DEX", "Barkskin: AC at least 17"."""
    notes = []
    for label, m in _own_armor_modifiers(char):
        if isinstance(m, ArmorClass):
            notes.append(f"{label}: {m.bonus:+d} AC")
        elif isinstance(m, ArmorClassBase):
            added = "".join(f" + {a.short_name}" for a in m.abilities)
            notes.append(f"{label}: base AC {m.base}{added}")
        elif isinstance(m, ArmorClassMinimum):
            notes.append(f"{label}: AC at least {m.value}")
    return notes


def _hit_point_changes(char: dict) -> list[tuple[str, HitPointMaximum]]:
    """The HitPointMaximum modifiers on char that count, each once: two of
    the same effect don't add up (Combining Game Effects). One not rolled
    yet (dice, an upcast) counts nothing: a badge keeps its number."""
    seen: list[tuple[str, HitPointMaximum]] = []
    for source, modifier in modifiers_on(char):
        if isinstance(modifier, HitPointMaximum) and modifier.rolled:
            pair = (_label(source), modifier)
            if pair not in seen:
                seen.append(pair)
    return seen


def hit_point_maximum(char: dict) -> int:
    """Char's Hit Point maximum with what its effects do to it (Aid's +5):
    its stored `max_hp` is the one without them, so it comes back when they
    end, and a player's sheet is never changed. Never below 0."""
    changes = sum(int(m.amount) for _, m in _hit_point_changes(char))
    return max(char.get("max_hp", 0) + changes, 0)


def hit_point_maximum_notes(char: dict) -> list[str]:
    """What changes char's Hit Point maximum: "Aid: +5"."""
    return [f"{label}: {int(m.amount):+d}" for label, m in _hit_point_changes(char)]


def hit_point_maximum_text(char: dict) -> str:
    """Char's Hit Point maximum with what changes it, "35 (30; Aid +5)", or
    "" when nothing does."""
    changes = [f"{label} {int(m.amount):+d}" for label, m in _hit_point_changes(char)]
    if not changes:
        return ""
    return f"{hit_point_maximum(char)} ({char.get('max_hp', 0)}; {', '.join(changes)})"


_Kind = TypeVar("_Kind")


def _counted_once(char: dict, kind: type[_Kind]) -> list[tuple[str, _Kind]]:
    """The modifiers of `kind` on char, by what gives each, each once: two of
    the same effect don't add up (Combining Game Effects)."""
    seen: list[tuple[str, _Kind]] = []
    for source, modifier in modifiers_on(char):
        if isinstance(modifier, kind) and (_label(source), modifier) not in seen:
            seen.append((_label(source), modifier))
    return seen


def _speed_steps(char: dict) -> list[tuple[str, Speed]]:
    """The Speed modifiers that make char's speeds, in the order they count:
    every bonus, then every multiplier; or only the lowest set_to, which
    no other changes."""
    pairs = _counted_once(char, Speed)
    fixed = [(m.set_to, label, m) for label, m in pairs if m.set_to is not None]
    if fixed:
        _, label, lowest = min(fixed, key=lambda entry: entry[0])
        return [(label, lowest)]
    return sorted(pairs, key=lambda pair: pair[1].multiplier != 1)


def speed_in_use(char: dict, stored: int) -> int:
    """One of char's speeds (its Speed, or its Fly Speed, ...) from the one
    it has (`stored`, its stat block's or sheet's), with its modifiers: the
    Rules Glossary has every special speed change as its Speed does. Never
    below 0, and rounded down."""
    steps = _speed_steps(char)
    if steps and steps[0][1].set_to is not None:
        return steps[0][1].set_to
    speed = stored + sum(m.bonus for _, m in steps)
    for _, m in steps:
        speed *= m.multiplier
    return max(int(speed), 0)


def _times(multiplier: int | float) -> str:
    if multiplier == 0.5:
        return "halved"
    return f"×{multiplier:g}"


def speed_changes(char: dict) -> list[str]:
    """What changes char's speeds, in the order it counts: "Longstrider +10
    ft.", "Haste ×2", "Haste 0 ft."."""
    changes = []
    for label, m in _speed_steps(char):
        if m.set_to is not None:
            changes.append(f"{label} {m.set_to} ft.")
        else:
            if m.bonus:
                changes.append(f"{label} {m.bonus:+d} ft.")
            if m.multiplier != 1:
                changes.append(f"{label} {_times(m.multiplier)}")
    return changes


SIZES = tuple(CreatureSize)


def _stored_size(char: dict) -> CreatureSize | None:
    """Char's own size: a monster's card keeps its CreatureSize, a player's
    and a log's its text ("Medium"). None when it isn't known."""
    try:
        return CreatureSize(char["size"]) if char.get("size") else None
    except ValueError:
        return None


def _size_steps(char: dict) -> tuple[CreatureSize | None, list[str]]:
    """Char's size with its modifiers (size_in_use), and what made it that:
    "Large Form", "Enlarge +1"."""
    size, changes = _stored_size(char), []
    pairs = _counted_once(char, Size)
    for label, m in pairs:
        if m.becomes is not None:
            size = m.becomes
            changes.append(label)
    for label, m in pairs:
        if m.steps:
            changes.append(f"{label} {m.steps:+d}")
            if size is not None:
                at = SIZES.index(size) + m.steps
                size = SIZES[min(max(at, 0), len(SIZES) - 1)]
    return size, changes


def size_in_use(char: dict) -> CreatureSize | None:
    """Char's size now: its own, or the one a Size it has makes it (Large
    Form's Large, then Enlarge's one larger). None when it isn't known, as
    when it only has steps and no size of its own."""
    return _size_steps(char)[0]


def size_text(char: dict) -> str:
    """Char's size with what changes it, "Large (Medium; Enlarge +1)", or
    "" when nothing does, or when the size isn't known (steps from a size
    nobody gave it): its badge is on its card anyway. "Large (Large Form)"
    when only what changes it gives it a size."""
    size, changes = _size_steps(char)
    if not changes or size is None:
        return ""
    stored = _stored_size(char)
    was = f"{stored.value}; " if stored is not None else ""
    return f"{size.value} ({was}{', '.join(changes)})"


def rolled_modifiers(
    modifiers: Iterable[Modifier], levels_up: int, roll: Callable[[str], int]
) -> tuple[Modifier, ...]:
    """`modifiers` as a badge keeps them once given: a HitPointMaximum's
    dice rolled with `roll` and its upcast added for each of `levels_up`
    slot levels above the spell's (Aid at level 3: 5 + 5), and a WhenHit
    keeps `levels_up` for the effect it uses (Armor of Agathys' Cold damage).
    The rest as they are."""
    kept: list[Modifier] = []
    for modifier in modifiers:
        if isinstance(modifier, WhenHit):
            kept.append(replace(modifier, levels_up=levels_up))
            continue
        if not isinstance(modifier, HitPointMaximum) or modifier.rolled:
            kept.append(modifier)
            continue
        sign = -1 if modifier.amount.startswith("-") else 1
        total = sign * roll(modifier.amount.lstrip("-"))
        if modifier.upcast:
            total += sign * sum(roll(modifier.upcast) for _ in range(levels_up))
        if total:
            kept.append(HitPointMaximum(str(total)))
    return tuple(kept)


def _damage_modifier(char: dict, kind: type, damage_type: str) -> bool:
    """Whether a modifier of `kind` (Resistance, DamageImmunity,
    Vulnerability) on char covers `damage_type`: none listed means all."""
    return any(
        isinstance(m, (Resistance, DamageImmunity, Vulnerability))
        and type(m) is kind
        and (not m.damage_types or any(t.value == damage_type for t in m.damage_types))
        for _, m in modifiers_on(char)
    )


def resists(char: dict, damage_type: str) -> bool:
    """Whether char's modifiers give it Resistance to `damage_type`."""
    return _damage_modifier(char, Resistance, damage_type)


def immune_to_damage(char: dict, damage_type: str) -> bool:
    """Whether char's modifiers give it Immunity to `damage_type`."""
    return _damage_modifier(char, DamageImmunity, damage_type)


def vulnerable_to(char: dict, damage_type: str) -> bool:
    """Whether char's modifiers give it Vulnerability to `damage_type`."""
    return _damage_modifier(char, Vulnerability, damage_type)


def resists_all_damage(char: dict) -> bool:
    """Whether char's modifiers give it Resistance to all damage (Petrified):
    then a resisted hit says nothing about its own defenses."""
    return any(
        isinstance(m, Resistance) and not m.damage_types for _, m in modifiers_on(char)
    )


# The card's words for each kind of damage defense, the order it lists them.
DEFENSE_WORDS: tuple[tuple[type, str], ...] = (
    (Vulnerability, "Vulnerable"),
    (Resistance, "Resist"),
    (DamageImmunity, "Immune"),
)


def defenses_from_modifiers(char: dict) -> dict[str, list[str]]:
    """The damage defenses and condition immunities char's modifiers give,
    by the card's word for them, each with where it comes from, once:
    {"Resist": ["Bludgeoning, Piercing, Slashing (Rage)"], "Cond. Immune":
    ["Frightened (Heroism)"]}. None listed is all damage (Petrified)."""
    found: dict[str, list[str]] = {}
    for source, m in modifiers_on(char):
        if isinstance(m, ConditionImmunity):
            word, names = "Cond. Immune", [c.value for c in m.conditions]
        elif isinstance(m, (Resistance, DamageImmunity, Vulnerability)):
            word = next(w for kind, w in DEFENSE_WORDS if type(m) is kind)
            names = [t.value for t in m.damage_types] or ["all damage"]
        else:
            continue
        text = f"{', '.join(names)} ({_label(source)})"
        if text not in found.setdefault(word, []):
            found[word].append(text)
    return found


def immune_to_condition(char: dict, condition: str) -> bool:
    """Whether char's modifiers make it immune to `condition` (Petrified's
    Poisoned): then that says nothing about its own immunities."""
    return any(
        isinstance(m, ConditionImmunity)
        and any(c.value == condition for c in m.conditions)
        for _, m in modifiers_on(char)
    )
