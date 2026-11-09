"""The rules conditions as data: what each does, sentence by sentence, in the
CombatModifiers vocabulary, from the 2024 Rules Glossary
(SourceTexts/RulesGlossary/Conditions/). The combat simulator reads the rolls,
AC and damage from it (Combat/Effects/); the rest is Notes."""

from Core.Definitions import Ability, Condition
from Model.Content.CombatModifiers import (
    D20_TESTS,
    AttacksAgainst,
    AutoFail,
    ConditionImmunity,
    CriticalHitsAgainst,
    D20Bonus,
    D20Mode,
    D20Test,
    HasConditions,
    Modifier,
    Note,
    Resistance,
    RollMode,
)

ADVANTAGE = RollMode.ADVANTAGE
DISADVANTAGE = RollMode.DISADVANTAGE
ATTACK_ROLL = D20Test.ATTACK_ROLL
SAVING_THROW = D20Test.SAVING_THROW
ABILITY_CHECK = D20Test.ABILITY_CHECK
INITIATIVE = D20Test.INITIATIVE

_SPEED_0 = Note("Speed 0: its Speed is 0 and can't increase.")
_WITHIN_5_FEET = "the attacker is within 5 feet of it"
_STRENGTH_AND_DEXTERITY = (Ability.STRENGTH, Ability.DEXTERITY)
_FAILS_STRENGTH_AND_DEXTERITY_SAVES = AutoFail((SAVING_THROW,), _STRENGTH_AND_DEXTERITY)

CONDITION_RULES: dict[Condition, tuple[Modifier, ...]] = {
    Condition.BLINDED: (
        Note("Can't See: it can't see."),
        AutoFail((ABILITY_CHECK,), when="the check requires sight"),
        AttacksAgainst(ADVANTAGE),
        D20Mode((ATTACK_ROLL,), DISADVANTAGE),
    ),
    Condition.CHARMED: (
        Note(
            "Can't Harm the Charmer: it can't attack the charmer or target the"
            " charmer with damaging abilities or magical effects."
        ),
        Note(
            "Social Advantage: the charmer has Advantage on any ability check to"
            " interact with it socially."
        ),
    ),
    Condition.DEAFENED: (
        Note("Can't Hear: it can't hear."),
        AutoFail((ABILITY_CHECK,), when="the check requires hearing"),
    ),
    Condition.EXHAUSTION: (
        Note(
            "Exhaustion Levels: each time it gets this condition, it gains a"
            " level; it dies at level 6."
        ),
        D20Bonus(D20_TESTS, "-2", per_level=True),
        Note("Speed Reduced: its Speed is 5 feet lower for each level."),
        Note("A Long Rest removes 1 level; at level 0 the condition ends."),
    ),
    Condition.FRIGHTENED: (
        D20Mode(
            (ABILITY_CHECK, ATTACK_ROLL),
            DISADVANTAGE,
            when="the source of fear is within line of sight",
        ),
        Note("Can't Approach: it can't willingly move closer to the source of fear."),
    ),
    Condition.GRAPPLED: (
        _SPEED_0,
        D20Mode((ATTACK_ROLL,), DISADVANTAGE, when="the target isn't the grappler"),
        Note(
            "Movable: the grappler can drag or carry it, each foot costing 1"
            " extra foot unless it is Tiny or two or more sizes smaller."
        ),
    ),
    Condition.INCAPACITATED: (
        Note("Inactive: it can't take any action, Bonus Action, or Reaction."),
        Note("No Concentration: its Concentration is broken."),
        Note("Speechless: it can't speak."),
        D20Mode((INITIATIVE,), DISADVANTAGE),
    ),
    Condition.INVISIBLE: (
        D20Mode((INITIATIVE,), ADVANTAGE),
        Note(
            "Concealed: it isn't affected by any effect that requires its target"
            " to be seen unless the effect's creator can somehow see it. Its"
            " equipment is concealed too."
        ),
        AttacksAgainst(DISADVANTAGE, when="the attacker can't see it"),
        D20Mode((ATTACK_ROLL,), ADVANTAGE, when="the target can't see it"),
    ),
    Condition.PARALYZED: (
        HasConditions((Condition.INCAPACITATED,)),
        _SPEED_0,
        _FAILS_STRENGTH_AND_DEXTERITY_SAVES,
        AttacksAgainst(ADVANTAGE),
        CriticalHitsAgainst(when=_WITHIN_5_FEET),
    ),
    Condition.PETRIFIED: (
        Note(
            "Turned to Inanimate Substance: it and its nonmagical gear become"
            " stone (usually); its weight is ten times more and it stops aging."
        ),
        HasConditions((Condition.INCAPACITATED,)),
        _SPEED_0,
        AttacksAgainst(ADVANTAGE),
        _FAILS_STRENGTH_AND_DEXTERITY_SAVES,
        Resistance(),
        ConditionImmunity((Condition.POISONED,)),
    ),
    Condition.POISONED: (D20Mode((ATTACK_ROLL, ABILITY_CHECK), DISADVANTAGE),),
    Condition.PRONE: (
        Note(
            "Restricted Movement: it can only crawl, or spend half its Speed to"
            " stand up and end the condition (not with a Speed of 0)."
        ),
        D20Mode((ATTACK_ROLL,), DISADVANTAGE),
        AttacksAgainst(ADVANTAGE, when=_WITHIN_5_FEET),
        AttacksAgainst(DISADVANTAGE, when="the attacker is farther than 5 feet"),
    ),
    Condition.RESTRAINED: (
        _SPEED_0,
        AttacksAgainst(ADVANTAGE),
        D20Mode((ATTACK_ROLL,), DISADVANTAGE),
        D20Mode((SAVING_THROW,), DISADVANTAGE, (Ability.DEXTERITY,)),
    ),
    Condition.STUNNED: (
        HasConditions((Condition.INCAPACITATED,)),
        _FAILS_STRENGTH_AND_DEXTERITY_SAVES,
        AttacksAgainst(ADVANTAGE),
    ),
    Condition.UNCONSCIOUS: (
        HasConditions((Condition.INCAPACITATED, Condition.PRONE)),
        Note(
            "Inert: it drops whatever it's holding, and stays Prone when the"
            " condition ends."
        ),
        _SPEED_0,
        AttacksAgainst(ADVANTAGE),
        _FAILS_STRENGTH_AND_DEXTERITY_SAVES,
        CriticalHitsAgainst(when=_WITHIN_5_FEET),
        Note("Unaware: it's unaware of its surroundings."),
    ),
}


def conditions_with(condition: Condition) -> frozenset[Condition]:
    """The conditions that are `condition` or give it, however indirectly:
    for Incapacitated, also Paralyzed, Petrified, Stunned and Unconscious."""
    return frozenset(c for c in Condition if condition in conditions_given_by(c))


def conditions_given_by(condition: Condition) -> list[Condition]:
    """`condition` and every condition it gives, in the order the rules name
    them: Unconscious, Incapacitated, Prone."""
    given = [condition]
    for held in given:
        for modifier in CONDITION_RULES[held]:
            if isinstance(modifier, HasConditions):
                given += [c for c in modifier.conditions if c not in given]
    return given
