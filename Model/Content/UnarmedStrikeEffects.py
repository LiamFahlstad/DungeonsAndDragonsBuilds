"""What an Unarmed Strike's Shove does in a fight, as combat effects (arena
plan, step 21): two rows after the Unarmed Strike's own attack, "Unarmed
Strike: Shove (push)" and "Unarmed Strike: Shove (Prone)", one for each
choice the Rules Glossary gives.

Rules Glossary, Unarmed Strike: "Shove. The target must succeed on a
Strength or Dexterity saving throw (it chooses which), or you either push it 5
feet away or cause it to have the Prone condition. The DC for the saving
throw equals 8 plus your Strength modifier and Proficiency Bonus. This
shove is possible only if the target is no more than one size larger than
you." Martial Arts lets a Monk use Dexterity for that DC, which the Unarmed
Strike's own ability (`attack_ability_modifier`) already is for one.

The Damage choice is the weapon's row; Grapple isn't here yet (the arena
plan's Later: grappling moves the Grappled creature). Nothing here imports
Combat."""

from Core.Definitions import Ability, Condition
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatEffect,
    CombatPush,
    EffectRoll,
)
from Model.Content.Weapon import AbstractWeapon
from Model.View import CharacterView

SHOVE_PUSH = "Unarmed Strike: Shove (push)"
SHOVE_PRONE = "Unarmed Strike: Shove (Prone)"

UNARMED_STRIKE_RULES = (
    "Instead of using a weapon to make a melee attack, you can use a punch,"
    " kick, headbutt, or similar forceful blow. In game terms, this is an"
    " Unarmed Strike—a melee attack that involves you using your body to"
    " damage, grapple, or shove a target within 5 feet of you.\n"
    "Shove. The target must succeed on a Strength or Dexterity saving throw"
    " (it chooses which), or you either push it 5 feet away or cause it to"
    " have the Prone condition. The DC for the saving throw equals 8 plus"
    " your Strength modifier and Proficiency Bonus. This shove is possible"
    " only if the target is no more than one size larger than you."
)

_NOTES = (
    "It chooses Strength or Dexterity: switch the ability if it picks"
    " Dexterity. Only a target within 5 feet and no more than one size"
    " larger than you.",
)


def shove_effects(
    weapon: AbstractWeapon, character: CharacterView
) -> list[CombatEffect]:
    """The Shove's two rows for the wielder of `weapon`, an Unarmed Strike,
    with its DC worked out (8 + the Unarmed Strike's ability modifier +
    Proficiency Bonus)."""
    dc = 8 + weapon.attack_ability_modifier(character)
    dc += character.get_proficiency_bonus()

    def shove(
        name: str,
        push: CombatPush | None = None,
        conditions: tuple[CombatCondition, ...] = (),
    ) -> CombatEffect:
        return CombatEffect(
            name=name,
            roll=EffectRoll.SAVE,
            save_ability=Ability.STRENGTH,
            dc=dc,
            conditions=conditions,
            spends_use=False,
            notes=_NOTES,
            push=push,
        )

    return [
        shove(SHOVE_PUSH, push=CombatPush(5)),
        shove(SHOVE_PRONE, conditions=(CombatCondition(Condition.PRONE),)),
    ]
