"""What something a creature has does to the rolls made by or against it, its
Armor Class and the damage it takes, while it has it: the vocabulary of lasting
effects (Notes/combat-effects-plan.md, Phase 3). The rules conditions are
written in it (Model/Content/RulesConditions.py); spells and features will be
too. The combat simulator reads it (Combat/Effects/), so content never imports
Combat. A badge's triggers (AtTurnStart, AtTurnEnd: what it does as a turn
starts or ends) are in the same list, as they are what it does too.

Each modifier is what one sentence of the rules says. One the simulator can't
decide by itself, because it depends on where creatures are or what they can
see, has a `when`, said as what follows "if" ("the attacker is within 5
feet"): it is never counted, only shown to the GM next to the roll. Anything
that changes no roll, AC or damage is a Note.

modifier_to_dict() and modifier_from_dict() are a modifier as plain data, the
way a fight's log keeps the ones a lasting effect gives (Bless's D20Bonus):
its type's name and the fields not at their default, enums as their values,

    {"type": "D20Bonus", "tests": ["attack roll", "saving throw"], "amount": "1d4"}
"""

import re
from dataclasses import dataclass, fields
from enum import Enum, StrEnum
from typing import Any, NoReturn

from Core.Definitions import Ability, Condition, DamageType

# A D20Bonus's amount: dice or a number, with a sign or without ("1d4",
# "-1d4", "-2", "+5").
BONUS_AMOUNT = re.compile(r"[+-]?(?:\d+d\d+|\d+)")
# Extra damage a hit deals: dice or a number, never less ("1d6", "2").
EXTRA_DAMAGE_AMOUNT = re.compile(r"[1-9]\d*d[1-9]\d*|[1-9]\d*")


class D20Test(StrEnum):
    """The d20 rolls a modifier changes. Initiative is a Dexterity check, but
    the rules name it on its own (Incapacitated, Invisible)."""

    ATTACK_ROLL = "attack roll"
    SAVING_THROW = "saving throw"
    ABILITY_CHECK = "ability check"
    INITIATIVE = "initiative"


# Every D20 Test, which is what the rules mean by "D20 Tests" (Exhaustion).
D20_TESTS = (D20Test.ATTACK_ROLL, D20Test.SAVING_THROW, D20Test.ABILITY_CHECK)


class RollMode(StrEnum):
    """Two d20s, the higher or the lower counting. The same text as the
    combat UI's roll modes, so they compare equal."""

    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"


def _check_tests(tests: tuple[D20Test, ...], abilities: tuple[Ability, ...]):
    if not tests:
        raise ValueError("A modifier on d20 rolls needs at least one D20Test")
    if abilities and not set(tests) <= {
        D20Test.SAVING_THROW,
        D20Test.ABILITY_CHECK,
    }:
        raise ValueError("Only saving throws and ability checks have abilities")


@dataclass(frozen=True)
class D20Mode:
    """Its own `tests` have Advantage or Disadvantage: of these `abilities`
    only, if any are given ("Disadvantage on Dexterity saving throws")."""

    tests: tuple[D20Test, ...]
    mode: RollMode
    abilities: tuple[Ability, ...] = ()
    when: str = ""

    def __post_init__(self):
        _check_tests(self.tests, self.abilities)


@dataclass(frozen=True)
class AttacksAgainst:
    """Attack rolls against it have Advantage or Disadvantage."""

    mode: RollMode
    when: str = ""


@dataclass(frozen=True)
class AutoFail:
    """It automatically fails its `tests` (of these `abilities`, if given)."""

    tests: tuple[D20Test, ...]
    abilities: tuple[Ability, ...] = ()
    when: str = ""

    def __post_init__(self):
        _check_tests(self.tests, self.abilities)


@dataclass(frozen=True)
class D20Bonus:
    """A number or dice added to its `tests`: "1d4" (Bless), "-1d4" (Bane),
    "-2". `per_level`: that much for each level it has (Exhaustion)."""

    tests: tuple[D20Test, ...]
    amount: str
    abilities: tuple[Ability, ...] = ()
    per_level: bool = False
    when: str = ""

    def __post_init__(self):
        _check_tests(self.tests, self.abilities)
        if not BONUS_AMOUNT.fullmatch(self.amount):
            raise ValueError(
                f"A D20Bonus needs an amount like '1d4', '-1d4' or '-2',"
                f" got {self.amount!r}"
            )


@dataclass(frozen=True)
class CriticalHitsAgainst:
    """An attack roll that hits it is a Critical Hit."""

    when: str = ""


@dataclass(frozen=True)
class ArmorClass:
    """What it adds to its AC (Shield of Faith's 2)."""

    bonus: int


@dataclass(frozen=True)
class Resistance:
    """Resistance to damage of these types; to all damage if none are given."""

    damage_types: tuple[DamageType, ...] = ()


class AttackKind(StrEnum):
    """The attacks something comes with: any attack roll's (Hunter's Mark,
    Hex), or only a weapon attack's, "an attack roll made with a weapon"
    (Divine Favor), which an Unarmed Strike or a spell attack isn't. A
    trigger (CombatTriggers.py) can also ask for a melee or a ranged attack,
    an Unarmed Strike or a spell attack; extra damage takes ANY and WEAPON
    only, which is all hit_plan reads."""

    ANY = "attack roll"
    WEAPON = "weapon attack"
    MELEE = "melee attack"
    RANGED = "ranged attack"
    UNARMED = "unarmed strike"
    SPELL = "spell attack"


# What extra damage can come with: hit_plan reads no other kind.
EXTRA_DAMAGE_ATTACKS = (AttackKind.ANY, AttackKind.WEAPON)


def _check_extra_damage(modifier):
    name = type(modifier).__name__
    if not isinstance(modifier.amount, str) or not EXTRA_DAMAGE_AMOUNT.fullmatch(
        modifier.amount
    ):
        raise ValueError(
            f"A {name} needs an amount like '1d6' or '2', got {modifier.amount!r}"
        )
    if not isinstance(modifier.damage_type, DamageType):
        raise ValueError(
            f"A {name} needs a DamageType, like DamageType.FORCE,"
            f" got {modifier.damage_type!r}"
        )
    if not isinstance(modifier.attacks, AttackKind):
        raise ValueError(
            f"A {name}'s attacks is an AttackKind, got {modifier.attacks!r}"
        )
    if modifier.attacks not in EXTRA_DAMAGE_ATTACKS:
        raise ValueError(
            f"A {name}'s attacks is {AttackKind.ANY.name} or"
            f" {AttackKind.WEAPON.name}, got {modifier.attacks.name}"
        )


@dataclass(frozen=True)
class ExtraDamageFrom:
    """On the target: hits on it by whoever gave it the effect this is on
    (its caster) deal `amount` more `damage_type` damage, with `attacks` of
    that kind: Hunter's Mark's 1d6 Force, Hex's 1d6 Necrotic. Its dice are
    doubled on a Critical Hit, as the attack's own are."""

    amount: str
    damage_type: DamageType
    attacks: AttackKind = AttackKind.ANY
    when: str = ""

    def __post_init__(self):
        _check_extra_damage(self)


@dataclass(frozen=True)
class ExtraDamageOnHit:
    """On the attacker: its hits deal `amount` more `damage_type` damage,
    with `attacks` of that kind: Divine Favor's 1d4 Radiant with weapons.
    Its dice are doubled on a Critical Hit, as the attack's own are."""

    amount: str
    damage_type: DamageType
    attacks: AttackKind = AttackKind.ANY
    when: str = ""

    def __post_init__(self):
        _check_extra_damage(self)


@dataclass(frozen=True)
class ConditionImmunity:
    """It can't be given these conditions while it has this."""

    conditions: tuple[Condition, ...]


@dataclass(frozen=True)
class HasConditions:
    """It has these conditions too, with all they do ("You have the
    Incapacitated condition")."""

    conditions: tuple[Condition, ...]


@dataclass(frozen=True)
class Note:
    """What it does that the simulator doesn't work out: shown, not counted."""

    text: str


class WhoseTurn(StrEnum):
    """The turns a trigger comes with: those of whoever has the badge
    (Heroism's target), or those of each creature not on its side (Spirit
    Guardians, on its caster, for the creatures around it)."""

    BEARER = "bearer"
    ENEMY = "enemy"


def _check_trigger(trigger):
    name = type(trigger).__name__
    if not isinstance(trigger.effect, str) or not trigger.effect.strip():
        raise ValueError(f"An {name} needs the name of the effect it uses")
    if not isinstance(trigger.whose, WhoseTurn):
        raise ValueError(f"An {name}'s whose is a WhoseTurn, got {trigger.whose!r}")


@dataclass(frozen=True)
class AtTurnStart:
    """As each turn of `whose` starts, the badge's caster uses `effect` (the
    name of another of its source's combat effects, one that spends no use)
    on whoever's turn it is: Heroism's Temporary Hit Points. The simulator
    gives Hit Points itself; an effect that rolls or deals damage, or one with
    a `when` (said as what follows "if": "it starts its turn in the
    Emanation"), is a prompt in the turn column, which opens the Custom
    Effect dialog with it picked."""

    effect: str
    whose: WhoseTurn = WhoseTurn.BEARER
    when: str = ""

    def __post_init__(self):
        _check_trigger(self)


@dataclass(frozen=True)
class AtTurnEnd:
    """The same as a turn of `whose` ends: Spirit Guardians' save for a
    creature that "ends its turn there"."""

    effect: str
    whose: WhoseTurn = WhoseTurn.BEARER
    when: str = ""

    def __post_init__(self):
        _check_trigger(self)


Trigger = AtTurnStart | AtTurnEnd
TRIGGER_CLASSES = (AtTurnStart, AtTurnEnd)

Modifier = (
    D20Mode
    | AttacksAgainst
    | AutoFail
    | D20Bonus
    | CriticalHitsAgainst
    | ArmorClass
    | Resistance
    | ExtraDamageFrom
    | ExtraDamageOnHit
    | ConditionImmunity
    | HasConditions
    | Note
    | AtTurnStart
    | AtTurnEnd
)
MODIFIER_TYPES: dict[str, type] = {
    cls.__name__: cls
    for cls in (
        D20Mode,
        AttacksAgainst,
        AutoFail,
        D20Bonus,
        CriticalHitsAgainst,
        ArmorClass,
        Resistance,
        ExtraDamageFrom,
        ExtraDamageOnHit,
        ConditionImmunity,
        HasConditions,
        Note,
        AtTurnStart,
        AtTurnEnd,
    )
}
MODIFIER_CLASSES = tuple(MODIFIER_TYPES.values())

# How each field is read back: a list of an enum's values, one value, or
# plain text, a number or a flag. A bool isn't a number here.
_ENUM_LISTS: dict[str, type[Enum]] = {
    "tests": D20Test,
    "abilities": Ability,
    "damage_types": DamageType,
    "conditions": Condition,
}
_ENUMS: dict[str, type[Enum]] = {
    "mode": RollMode,
    "damage_type": DamageType,
    "attacks": AttackKind,
    "whose": WhoseTurn,
}
_PLAIN: dict[str, type] = {
    "when": str,
    "amount": str,
    "text": str,
    "effect": str,
    "per_level": bool,
    "bonus": int,
}


def modifier_to_dict(modifier: Modifier) -> dict:
    """`modifier` as plain data (see the module docstring)."""
    data: dict[str, Any] = {"type": type(modifier).__name__}
    for field in fields(modifier):
        value = getattr(modifier, field.name)
        if value == field.default:
            continue
        if isinstance(value, tuple):
            data[field.name] = [item.value for item in value]
        elif isinstance(value, Enum):
            data[field.name] = value.value
        else:
            data[field.name] = value
    return data


def modifier_from_dict(data: Any, where: str = "a modifier") -> Modifier:
    """The modifier `data` says, as modifier_to_dict writes it. ValueError
    naming `where` and the field when anything is unknown, missing or of the
    wrong kind."""

    def fail(problem: str) -> NoReturn:
        raise ValueError(f"Invalid modifier of {where}: {problem}")

    def enum(kind: type[Enum], value: Any, name: str):
        try:
            return kind(value)
        except ValueError:
            fail(f"{name}: {value!r} is not one of {[m.value for m in kind]}")

    if not isinstance(data, dict):
        fail(f"expected an object, got {data!r}")
    cls = MODIFIER_TYPES.get(str(data.get("type")))
    if cls is None:
        fail(f"type {data.get('type')!r} is not one of {list(MODIFIER_TYPES)}")
    known = [field.name for field in fields(cls)]
    unknown = sorted(set(data) - {"type", *known})
    if unknown:
        fail(f"unknown key(s) {unknown} for a {cls.__name__}, known: {known}")
    values: dict[str, Any] = {}
    for name in known:
        if name not in data:
            continue
        value = data[name]
        if name in _ENUM_LISTS:
            if not isinstance(value, list):
                fail(f"{name}: expected a list, got {value!r}")
            values[name] = tuple(enum(_ENUM_LISTS[name], v, name) for v in value)
        elif name in _ENUMS:
            values[name] = enum(_ENUMS[name], value, name)
        else:
            kind = _PLAIN[name]
            if type(value) is not kind:
                fail(f"{name}: expected {kind.__name__}, got {value!r}")
            values[name] = value
    try:
        return cls(**values)
    except (TypeError, ValueError) as error:
        fail(str(error))
