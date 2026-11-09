"""What something a creature has does to the rolls made by or against it, its
Armor Class and the damage it takes, while it has it: the vocabulary of lasting
effects (Notes/combat-effects-plan.md, Phase 3). The rules conditions are
written in it (Model/Content/RulesConditions.py); spells and features will be
too. The combat simulator reads it (Combat/Effects/), so content never imports
Combat.

Each modifier is what one sentence of the rules says. One the simulator can't
decide by itself, because it depends on where creatures are or what they can
see, has a `when`, said as what follows "if" ("the attacker is within 5
feet"): it is never counted, only shown to the GM next to the roll. Anything
that changes no roll, AC or damage is a Note.
"""

from dataclasses import dataclass
from enum import StrEnum

from Core.Definitions import Ability, Condition, DamageType


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
        if not self.amount.lstrip("+-"):
            raise ValueError("A D20Bonus needs an amount, like '1d4' or '-2'")


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


Modifier = (
    D20Mode
    | AttacksAgainst
    | AutoFail
    | D20Bonus
    | CriticalHitsAgainst
    | ArmorClass
    | Resistance
    | ConditionImmunity
    | HasConditions
    | Note
)
