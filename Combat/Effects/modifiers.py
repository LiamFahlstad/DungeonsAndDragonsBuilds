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
attacker is the caster of the effect it's on. One with a `when` (where the attacker is, what it can see)
is never counted, only noted, since the simulator doesn't know positions
(plan principle 8). A total rolled at the table counts as it is, so only the
notes it can't have known about come with it. The roll modes are the UI's
text: "Neutral", "Advantage", "Disadvantage".
"""

from collections.abc import Iterable
from dataclasses import dataclass

from Core.Definitions import Ability, Condition
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
    Modifier,
    Resistance,
    RollMode,
    Vulnerability,
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
            if isinstance(m, AttacksAgainst)
        ]
    return _plan(mode, sources, D20Test.ATTACK_ROLL, None, typed)


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
    with it but isn't counted, for the GM."""

    extras: tuple[tuple[str, str, str], ...] = ()
    notes: tuple[str, ...] = ()


def hit_plan(
    attacker: dict | None, target: dict | None, weapon_attack: bool | None
) -> HitPlan:
    """The extra damage a hit by attacker on target deals (hit_extras).
    `weapon_attack`: whether the attack was made with a weapon, None when
    that isn't known (a monster's attack, a spell, an effect typed in).
    What only comes with a weapon attack adds nothing to one that isn't,
    and is noted, not counted, when that isn't known; one with a `when` is
    noted too (plan principle 8)."""
    extras: list[tuple[str, str, str]] = []
    notes: list[str] = []
    for label, modifier in hit_extras(attacker, target):
        weapons_only = modifier.attacks == AttackKind.WEAPON
        if weapons_only and weapon_attack is False:
            continue
        if modifier.when or (weapons_only and weapon_attack is None):
            notes.append(f"{label} (not counted): {extra_text(modifier)}")
        else:
            extras.append((label, modifier.amount, modifier.damage_type.value))
    return HitPlan(tuple(extras), tuple(notes))


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


def armor_class(char: dict, stored: int) -> int:
    """Char's AC with its modifiers in it, from the AC it has (`stored`: its
    stat block's or sheet's). The best of that and each ArmorClassBase, then
    what adds to it (ArmorClass), then at least each ArmorClassMinimum, and
    then its cover, which adds to whatever its AC is."""
    pairs = _own_armor_modifiers(char)
    armor = max(
        [stored]
        + [
            m.base + sum(_ability_bonus(char, a) for a in m.abilities)
            for _, m in pairs
            if isinstance(m, ArmorClassBase)
        ]
    )
    armor += sum(m.bonus for _, m in pairs if isinstance(m, ArmorClass))
    armor = max(
        [armor] + [m.value for _, m in pairs if isinstance(m, ArmorClassMinimum)]
    )
    return armor + cover_armor_bonus(char)


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


def immune_to_condition(char: dict, condition: str) -> bool:
    """Whether char's modifiers make it immune to `condition` (Petrified's
    Poisoned): then that says nothing about its own immunities."""
    return any(
        isinstance(m, ConditionImmunity)
        and any(c.value == condition for c in m.conditions)
        for _, m in modifiers_on(char)
    )
